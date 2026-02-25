"""
=============================================================
AgroSphere AI — Sentinel Hub API Integration Test
=============================================================
PURPOSE  : Validate Sentinel Hub OAuth2 auth, Process API
           satellite imagery fetching, and NDVI computation.
USAGE    : python test_sentinel_ndvi.py
NOTE     : Testing only — NOT integrated into FastAPI.
=============================================================
"""

import io
import os
import sys
import requests
import numpy as np
import rasterio
import matplotlib
matplotlib.use("Agg")           # headless-safe backend
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime, timedelta, timezone
import importlib
import json

# Force reload coordinates module to always get fresh values
import coordinates
importlib.reload(coordinates)
CENTER_LAT = coordinates.CENTER_LAT
CENTER_LON = coordinates.CENTER_LON
AREA_SIZE_KM = coordinates.AREA_SIZE_KM

# ─────────────────────────────────────────────
#  CONFIGURATION — fill in before running
# ─────────────────────────────────────────────
CLIENT_ID     = "89bd7c1b-891f-4548-af15-dd9c810176fe"   # Sentinel Hub client_id
CLIENT_SECRET = "T6ERA5e5VHP2KQphhc5AwNchqONQWgio"          # Sentinel Hub client_secret

# Choose input MODE:
#   "bbox"   → fill BBOX below
#   "center" → fill CENTER_LAT, CENTER_LON, AREA_KM below
INPUT_MODE = "center"

# Mode A — bounding box [minLon, minLat, maxLon, maxLat]
BBOX = [77.50, 12.85, 77.70, 13.05]       # example: Bengaluru area

# Mode B — centre-point + radius in km
# Import coordinates from coordinates.py file
from coordinates import CENTER_LAT, CENTER_LON, AREA_SIZE_KM
 
# Imagery settings
RESOLUTION   = 256                         # pixels per side
DAYS_BACK    = 30                          # look-back window

# Sentinel Hub OAuth2 / Process API endpoints
TOKEN_URL = "https://services.sentinel-hub.com/oauth/token"
PROCESS_URL = "https://services.sentinel-hub.com/api/v1/process"

# Output directory (same folder as this script)
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ─────────────────────────────────────────────
#  1. AUTHENTICATION
# ─────────────────────────────────────────────
def get_access_token() -> str:
    """
    Authenticate with Sentinel Hub via OAuth2 client-credentials flow.
    Returns the bearer access token string.
    """
    print("\n[AUTH] Requesting access token …")
    try:
        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type":    "client_credentials",
                "client_id":     CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
            timeout=30,
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise ValueError("No 'access_token' field in response.")
        print("[AUTH] ✓ Access token generated successfully.")
        return token
    except requests.exceptions.HTTPError as e:
        print(f"[AUTH] ✗ HTTP error during authentication: {e}")
        print(f"        Response body: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"[AUTH] ✗ Authentication failed: {e}")
        sys.exit(1)


# ─────────────────────────────────────────────
#  2. BOUNDING BOX HELPER
# ─────────────────────────────────────────────
def generate_bbox_from_center(
    lat: float, lon: float, area_km: float
) -> list[float]:
    """
    Generate a square bounding box [minLon, minLat, maxLon, maxLat]
    centred on (lat, lon) with side length area_km kilometres.
    Uses the flat-earth approximation (accurate to ~0.5 % at mid-latitudes).
    """
    half_km = area_km / 2.0
    # 1 degree latitude ≈ 111.32 km
    delta_lat = half_km / 111.32
    # 1 degree longitude ≈ 111.32 * cos(lat) km
    delta_lon = half_km / (111.32 * np.cos(np.radians(lat)))

    bbox = [
        round(lon - delta_lon, 6),   # minLond
        round(lat - delta_lat, 6),   # minLat
        round(lon + delta_lon, 6),   # maxLon
        round(lat + delta_lat, 6),   # maxLat
    ]
    print(f"[BBOX] Generated bounding box: {bbox}")
    return bbox


# ─────────────────────────────────────────────
#  3. SATELLITE DATA FETCH
# ─────────────────────────────────────────────
def fetch_satellite_data(token: str, bbox: list[float]) -> bytes:
    """
    Request Sentinel-2 L2A B04 + B08 imagery from Sentinel Hub Process API.
    Returns the raw GeoTIFF bytes on success.
    """
    now   = datetime.now(timezone.utc)
    start = (now - timedelta(days=DAYS_BACK)).strftime("%Y-%m-%dT00:00:00Z")
    end   = now.strftime("%Y-%m-%dT23:59:59Z")

    payload = {
        "input": {
            "bounds": {
                "bbox": bbox,
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
            },
            "data": [
                {
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {"from": start, "to": end},
                        "mosaickingOrder": "leastCC",   # pick least cloud cover
                    },
                }
            ],
        },
        "output": {
            "width":  RESOLUTION,
            "height": RESOLUTION,
            "responses": [
                {
                    "identifier": "default",
                    "format": {"type": "image/tiff"},
                }
            ],
        },
        "evalscript": """
//VERSION=3
function setup() {
  return {
    input: [{ bands: ["B04", "B08"] }],
    output: { bands: 2, sampleType: "FLOAT32" }
  };
}
function evaluatePixel(sample) {
  return [sample.B04, sample.B08];
}
""",
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
        "Accept":        "image/tiff",
    }

    print("\n[API] Sending satellite data request …")
    try:
        response = requests.post(
            PROCESS_URL,
            json=payload,
            headers=headers,
            timeout=120,
        )
        print(f"[API] Satellite API request status: {response.status_code}")
        response.raise_for_status()
        print("[API] ✓ Imagery data received.")
        return response.content
    except requests.exceptions.HTTPError as e:
        print(f"[API] ✗ HTTP error fetching imagery: {e}")
        print(f"       Response: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"[API] ✗ Request failed: {e}")
        sys.exit(1)


# ─────────────────────────────────────────────
#  4. BAND EXTRACTION
# ─────────────────────────────────────────────
def extract_bands(tiff_bytes: bytes) -> tuple[np.ndarray, np.ndarray]:
    """
    Load GeoTIFF bytes via rasterio and extract B04 (Red) + B08 (NIR) arrays.
    Returns (red_band, nir_band) as float32 numpy arrays.
    """
    print("\n[BANDS] Loading GeoTIFF …")
    try:
        with rasterio.open(io.BytesIO(tiff_bytes)) as src:
            print(f"[BANDS] ✓ GeoTIFF loaded successfully. "
                  f"Bands: {src.count}, Size: {src.width}×{src.height}")
            red_band = src.read(1).astype(np.float32)   # Band 1 → B04 (Red)
            nir_band = src.read(2).astype(np.float32)   # Band 2 → B08 (NIR)
            print("[BANDS] ✓ B04 (Red) and B08 (NIR) extracted.")
            return red_band, nir_band
    except Exception as e:
        print(f"[BANDS] ✗ Failed to extract bands: {e}")
        sys.exit(1)


# ─────────────────────────────────────────────
#  5. BAND STATISTICS
# ─────────────────────────────────────────────
def print_band_statistics(red_band: np.ndarray, nir_band: np.ndarray) -> None:
    """Print summary statistics for both spectral bands."""
    print("\n" + "─" * 50)
    print("  Band Statistics")
    print("─" * 50)
    print(f"  B04 (Red) → Min: {np.nanmin(red_band):.4f}, "
          f"Max: {np.nanmax(red_band):.4f}, "
          f"Mean: {np.nanmean(red_band):.4f}")
    print(f"  B08 (NIR) → Min: {np.nanmin(nir_band):.4f}, "
          f"Max: {np.nanmax(nir_band):.4f}, "
          f"Mean: {np.nanmean(nir_band):.4f}")
    print("─" * 50)


# ─────────────────────────────────────────────
#  6. NDVI COMPUTATION
# ─────────────────────────────────────────────
def compute_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
    """
    Compute NDVI = (NIR - Red) / (NIR + Red).
    Handles divide-by-zero (result set to NaN).
    Reflectance values >1 are clipped assuming raw DN — apply /10000 scaling.
    """
    print("\n[NDVI] Computing NDVI …")

    # Sentinel-2 L2A reflectance is stored as raw DN (0–10000 range).
    # If values exceed 1.0 we assume DN encoding and scale accordingly.
    if np.nanmax(red_band) > 1.0 or np.nanmax(nir_band) > 1.0:
        print("[NDVI]  → Detected DN-encoded values (>1.0). "
              "Scaling bands by ÷ 10000.")
        red_band = red_band / 10000.0
        nir_band = nir_band / 10000.0

    numerator   = nir_band - red_band
    denominator = nir_band + red_band

    # Suppress true divide warnings — we handle them manually via np.where
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = np.where(denominator != 0, numerator / denominator, np.nan)

    ndvi = ndvi.astype(np.float32)
    print("[NDVI] ✓ NDVI computed.")
    return ndvi


# ─────────────────────────────────────────────
#  7. NDVI STATISTICS
# ─────────────────────────────────────────────
def print_ndvi_statistics(ndvi: np.ndarray) -> None:
    """Print summary statistics for the computed NDVI array."""
    valid = ndvi[~np.isnan(ndvi)]
    print("\n" + "─" * 50)
    print("  NDVI Statistics")
    print("─" * 50)
    if valid.size == 0:
        print("  ⚠ No valid (non-NaN) NDVI pixels found.")
    else:
        print(f"  Min NDVI  : {np.min(valid):.4f}")
        print(f"  Max NDVI  : {np.max(valid):.4f}")
        print(f"  Mean NDVI : {np.mean(valid):.4f}")
        print(f"  Valid px  : {valid.size} / {ndvi.size}")
    print("─" * 50)


# ─────────────────────────────────────────────
#  8. SAVE OUTPUTS
# ─────────────────────────────────────────────
def save_outputs(
    tiff_bytes: bytes,
    red_band:   np.ndarray,
    nir_band:   np.ndarray,
    ndvi:       np.ndarray,
) -> None:
    """
    Persist all output artefacts to OUTPUT_DIR:
      • red_band.tif    — single-band GeoTIFF
      • nir_band.tif    — single-band GeoTIFF
      • ndvi_map.png    — false-colour NDVI visualisation (RdYlGn colormap)
      • ndvi_raw.npy    — raw NDVI numpy array
    """
    print("\n[SAVE] Writing output files …")

    # ── Read metadata from original multi-band TIFF ──────────────────────
    with rasterio.open(io.BytesIO(tiff_bytes)) as src:
        profile = src.profile.copy()
        transform = src.transform
        crs = src.crs

    single_band_profile = profile.copy()
    single_band_profile.update(count=1, dtype="float32", driver="GTiff")

    # ── red_band.tif ──────────────────────────────────────────────────────
    red_path = os.path.join(OUTPUT_DIR, "red_band.tif")
    with rasterio.open(red_path, "w", **single_band_profile) as dst:
        dst.write(red_band, 1)
    print(f"[SAVE]  ✓ red_band.tif  → {red_path}")

    # ── nir_band.tif ──────────────────────────────────────────────────────
    nir_path = os.path.join(OUTPUT_DIR, "nir_band.tif")
    with rasterio.open(nir_path, "w", **single_band_profile) as dst:
        dst.write(nir_band, 1)
    print(f"[SAVE]  ✓ nir_band.tif  → {nir_path}")

    # ── ndvi_map.png ──────────────────────────────────────────────────────
    ndvi_png_path = os.path.join(OUTPUT_DIR, "ndvi_map.png")
    fig, ax = plt.subplots(figsize=(7, 7))
    cmap = plt.get_cmap("RdYlGn")
    cmap.set_bad(color="black")         # NaN pixels rendered black

    img = ax.imshow(ndvi, cmap=cmap, vmin=-1.0, vmax=1.0)
    cbar = fig.colorbar(img, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("NDVI", fontsize=12)
    ax.set_title("Sentinel-2 NDVI Map\n(AgroSphere AI — Test)", fontsize=13)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(ndvi_png_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[SAVE]  ✓ ndvi_map.png  → {ndvi_png_path}")

    # ── ndvi_raw.npy ──────────────────────────────────────────────────────
    npy_path = os.path.join(OUTPUT_DIR, "ndvi_raw.npy")
    np.save(npy_path, ndvi)
    print(f"[SAVE]  ✓ ndvi_raw.npy  → {npy_path}")

    print("\n[SAVE] ✓ All output files saved successfully.")
    print("\nSaved:")
    print(f"  - red_band.tif")
    print(f"  - nir_band.tif")
    print(f"  - ndvi_map.png")
    print(f"  - ndvi_raw.npy")
    print(f"  - ndvi_analysis.json (will be generated next)")


# ─────────────────────────────────────────────
#  9. GENERATE JSON OUTPUT
# ─────────────────────────────────────────────
def generate_json_output(
    ndvi: np.ndarray,
    lat: float,
    lon: float,
    area_km: float
) -> dict:
    """
    Generate structured JSON output with NDVI statistics and vegetation analysis.
    
    Returns a dictionary with:
    - mean_ndvi, min_ndvi, max_ndvi
    - vegetation_coverage_percentage
    - healthy_percentage, stressed_percentage, non_vegetated_percentage
    - timestamp
    - location details
    """
    valid_ndvi = ndvi[~np.isnan(ndvi)]
    total_pixels = ndvi.size
    valid_pixels = valid_ndvi.size
    
    # Basic statistics
    mean_ndvi = float(np.mean(valid_ndvi)) if valid_pixels > 0 else 0.0
    min_ndvi = float(np.min(valid_ndvi)) if valid_pixels > 0 else 0.0
    max_ndvi = float(np.max(valid_ndvi)) if valid_pixels > 0 else 0.0
    
    # Vegetation classification
    # Non-vegetated: NDVI < 0.2
    # Stressed: 0.2 <= NDVI < 0.6
    # Healthy: NDVI >= 0.6
    non_vegetated = np.sum(valid_ndvi < 0.2)
    stressed = np.sum((valid_ndvi >= 0.2) & (valid_ndvi < 0.6))
    healthy = np.sum(valid_ndvi >= 0.6)
    
    # Calculate percentages
    non_vegetated_pct = (non_vegetated / total_pixels) * 100 if total_pixels > 0 else 0.0
    stressed_pct = (stressed / total_pixels) * 100 if total_pixels > 0 else 0.0
    healthy_pct = (healthy / total_pixels) * 100 if total_pixels > 0 else 0.0
    vegetation_coverage_pct = stressed_pct + healthy_pct
    
    # Generate timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Build output dictionary
    output = {
        "mean_ndvi": round(mean_ndvi, 4),
        "min_ndvi": round(min_ndvi, 4),
        "max_ndvi": round(max_ndvi, 4),
        "vegetation_coverage_percentage": round(vegetation_coverage_pct, 1),
        "healthy_percentage": round(healthy_pct, 1),
        "stressed_percentage": round(stressed_pct, 1),
        "non_vegetated_percentage": round(non_vegetated_pct, 1),
        "timestamp": timestamp,
        "location": {
            "lat": lat,
            "lon": lon,
            "area_km": area_km
        }
    }
    
    return output


def save_json_output(output: dict) -> None:
    """Save JSON output to file."""
    json_path = os.path.join(OUTPUT_DIR, "ndvi_analysis.json")
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[JSON]  ✓ ndvi_analysis.json → {json_path}")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main() -> None:
    print("=" * 58)
    print(" AgroSphere AI — Sentinel Hub Integration Test")
    print("=" * 58)

    # Guard: refuse to run with placeholder credentials
    if CLIENT_ID == "YOUR_CLIENT_ID" or CLIENT_SECRET == "YOUR_CLIENT_SECRET":
        print(
            "\n[CONFIG] ✗ Please replace CLIENT_ID and CLIENT_SECRET "
            "with your actual Sentinel Hub credentials before running.\n"
        )
        sys.exit(1)

    # --- Step 1: Authenticate ------------------------------------------------
    token = get_access_token()

    # --- Step 2: Resolve bounding box ----------------------------------------
    if INPUT_MODE == "center":
        print(f"\n[BBOX] Mode B: centre ({CENTER_LAT}, {CENTER_LON}), "
              f"area {AREA_SIZE_KM} km")
        bbox = generate_bbox_from_center(CENTER_LAT, CENTER_LON, AREA_SIZE_KM)
    else:
        print(f"\n[BBOX] Mode A: using supplied bbox {BBOX}")
        bbox = BBOX

    # --- Step 3: Fetch satellite data ----------------------------------------
    tiff_bytes = fetch_satellite_data(token, bbox)

    # --- Step 4: Extract bands ------------------------------------------------
    red_band, nir_band = extract_bands(tiff_bytes)

    # --- Step 5: Print band statistics ----------------------------------------
    print_band_statistics(red_band, nir_band)

    # --- Step 6: Compute NDVI -------------------------------------------------
    ndvi = compute_ndvi(red_band, nir_band)

    # --- Step 7: Print NDVI statistics ----------------------------------------
    print_ndvi_statistics(ndvi)

    # --- Step 8: Save all outputs ---------------------------------------------
    save_outputs(tiff_bytes, red_band, nir_band, ndvi)

    # --- Step 9: Generate and save JSON output --------------------------------
    print("\n[JSON] Generating structured output …")
    json_output = generate_json_output(ndvi, CENTER_LAT, CENTER_LON, AREA_SIZE_KM)
    save_json_output(json_output)
    
    # Print JSON to console
    print("\n" + "─" * 58)
    print("  JSON Output")
    print("─" * 58)
    print(json.dumps(json_output, indent=2))
    print("─" * 58)

    print("\n" + "=" * 58)
    print(" Test completed successfully.")
    print("=" * 58 + "\n")


if __name__ == "__main__":
    main()
