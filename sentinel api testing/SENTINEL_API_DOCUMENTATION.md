# AgroSphere AI — Sentinel Hub API Integration Documentation

**Version:** 1.0.0  
**Purpose:** Satellite Imagery Fetching & NDVI Computation  
**Status:** ✅ Tested & Operational  
**Last Updated:** February 22, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Configuration](#configuration)
5. [System Components](#system-components)
6. [Data Flow](#data-flow)
7. [NDVI Computation](#ndvi-computation)
8. [Usage Guide](#usage-guide)
9. [Output Files](#output-files)
10. [API Reference](#api-reference)
11. [Troubleshooting](#troubleshooting)
12. [Integration Notes](#integration-notes)

---

## Overview

The **Sentinel Hub API Integration** is a standalone Python script that validates satellite imagery fetching and NDVI (Normalized Difference Vegetation Index) computation for the AgroSphere AI platform.

### Key Features

✅ **OAuth2 Authentication** — Secure client-credentials flow with Sentinel Hub  
✅ **Sentinel-2 L2A Imagery** — Fetches B04 (Red) and B08 (NIR) bands  
✅ **Dual Input Modes** — Bounding box or center-point + radius  
✅ **NDVI Computation** — Automatic calculation with DN scaling  
✅ **Multi-format Output** — GeoTIFF bands, PNG visualization, NumPy array  
✅ **Comprehensive Statistics** — Band and NDVI min/max/mean values  
✅ **Error Handling** — Graceful failures with detailed error messages

### Design Purpose

This is a **TESTING SCRIPT ONLY** — not integrated into FastAPI backend.

It serves to:
- Validate Sentinel Hub API connectivity
- Test OAuth2 authentication flow
- Verify band extraction and NDVI computation
- Generate reference outputs for validation

---

## Architecture

### File Structure

```
sentinel api testing/
├── test_sentinel_ndvi.py           # Main test script
├── SENTINEL_API_DOCUMENTATION.md   # This file
├── red_band.tif                    # Output: Red band GeoTIFF
├── nir_band.tif                    # Output: NIR band GeoTIFF
├── ndvi_map.png                    # Output: NDVI visualization
└── ndvi_raw.npy                    # Output: Raw NDVI array
```

### Dependencies

```python
import requests      # HTTP requests for API calls
import rasterio      # GeoTIFF reading/writing
import numpy as np   # Array operations
import matplotlib    # Visualization
```

**Installation:**
```bash
pip install requests rasterio numpy matplotlib
```

---

## Prerequisites

### 1. Sentinel Hub Account

**Sign up:** https://www.sentinel-hub.com/

**Create OAuth Client:**
1. Log in to Sentinel Hub Dashboard
2. Navigate to "User Settings" → "OAuth clients"
3. Click "Create new OAuth client"
4. Note your `client_id` and `client_secret`

### 2. Python Environment

**Required Python version:** 3.8+

**Install dependencies:**
```bash
pip install requests rasterio numpy matplotlib
```

### 3. Credentials Configuration

Edit `test_sentinel_ndvi.py` and insert your credentials:

```python
CLIENT_ID     = "your-client-id-here"
CLIENT_SECRET = "your-client-secret-here"
```

⚠️ **Security Note:** Never commit credentials to version control!

---

## Configuration

### Input Modes

The script supports two input modes for defining the area of interest:

#### Mode A: Bounding Box


Directly specify geographic bounds:

```python
INPUT_MODE = "bbox"
BBOX = [77.50, 12.85, 77.70, 13.05]  # [minLon, minLat, maxLon, maxLat]
```

**Example:** Bengaluru area

#### Mode B: Center Point + Radius

Specify center coordinates and area size:

```python
INPUT_MODE = "center"
CENTER_LAT   = 20.5937  # Latitude
CENTER_LON   = 78.9629  # Longitude
AREA_SIZE_KM = 10.0     # Square side length in km
```

**Example:** 10km × 10km area centered on coordinates

The script automatically generates the bounding box using flat-earth approximation (accurate to ~0.5% at mid-latitudes).

### Imagery Settings

```python
RESOLUTION   = 256      # Pixels per side (256×256)
DAYS_BACK    = 30       # Look-back window for imagery
```

**Resolution Options:**
- `256` — Fast, suitable for testing
- `512` — Medium detail
- `1024` — High detail (slower)

**Time Window:**
- `DAYS_BACK = 30` — Last 30 days
- Sentinel Hub selects least cloudy image in this period

### API Endpoints

```python
TOKEN_URL   = "https://services.sentinel-hub.com/oauth/token"
PROCESS_URL = "https://services.sentinel-hub.com/api/v1/process"
```

---

## System Components

### 1. Authentication (`get_access_token()`)

**Purpose:** Authenticate with Sentinel Hub using OAuth2 client-credentials flow

**Process:**
1. Send POST request to token endpoint
2. Include `client_id` and `client_secret`
3. Receive `access_token` (valid for 1 hour)
4. Return bearer token string

**Error Handling:**
- HTTP errors → Print response body and exit
- Missing token field → Raise ValueError
- Network errors → Print exception and exit

**Output:**
```
[AUTH] Requesting access token …
[AUTH] ✓ Access token generated successfully.
```

### 2. Bounding Box Generation (`generate_bbox_from_center()`)

**Purpose:** Convert center point + radius to bounding box

**Algorithm:**
```python
# Flat-earth approximation
delta_lat = (area_km / 2) / 111.32
delta_lon = (area_km / 2) / (111.32 * cos(lat))

bbox = [
    lon - delta_lon,  # minLon
    lat - delta_lat,  # minLat
    lon + delta_lon,  # maxLon
    lat + delta_lat   # maxLat
]
```

**Accuracy:** ±0.5% at mid-latitudes (sufficient for agricultural fields)

**Output:**
```
[BBOX] Generated bounding box: [78.9179, 20.5487, 78.9629, 20.6387]
```


### 3. Satellite Data Fetch (`fetch_satellite_data()`)

**Purpose:** Request Sentinel-2 L2A imagery from Process API

**Request Payload:**
```json
{
  "input": {
    "bounds": {
      "bbox": [minLon, minLat, maxLon, maxLat],
      "properties": {"crs": "EPSG:4326"}
    },
    "data": [{
      "type": "sentinel-2-l2a",
      "dataFilter": {
        "timeRange": {"from": "...", "to": "..."},
        "mosaickingOrder": "leastCC"
      }
    }]
  },
  "output": {
    "width": 256,
    "height": 256,
    "responses": [{
      "identifier": "default",
      "format": {"type": "image/tiff"}
    }]
  },
  "evalscript": "..."
}
```

**Evalscript:**
```javascript
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
```

**Key Features:**
- `mosaickingOrder: "leastCC"` — Selects least cloudy image
- `sampleType: "FLOAT32"` — Preserves precision
- Returns 2-band GeoTIFF (B04, B08)

**Output:**
```
[API] Sending satellite data request …
[API] Satellite API request status: 200
[API] ✓ Imagery data received.
```

### 4. Band Extraction (`extract_bands()`)

**Purpose:** Load GeoTIFF and extract Red/NIR bands

**Process:**
1. Open GeoTIFF bytes with rasterio
2. Read band 1 → B04 (Red)
3. Read band 2 → B08 (NIR)
4. Convert to float32 arrays

**Output:**
```
[BANDS] Loading GeoTIFF …
[BANDS] ✓ GeoTIFF loaded successfully. Bands: 2, Size: 256×256
[BANDS] ✓ B04 (Red) and B08 (NIR) extracted.
```

**Returns:** `(red_band, nir_band)` as NumPy arrays

### 5. Band Statistics (`print_band_statistics()`)

**Purpose:** Display summary statistics for spectral bands

**Metrics:**
- Minimum value
- Maximum value
- Mean value

**Output:**
```
──────────────────────────────────────────────────
  Band Statistics
──────────────────────────────────────────────────
  B04 (Red) → Min: 0.0234, Max: 0.1456, Mean: 0.0823
  B08 (NIR) → Min: 0.1123, Max: 0.4567, Mean: 0.2891
──────────────────────────────────────────────────
```


### 6. NDVI Computation (`compute_ndvi()`)

**Purpose:** Calculate Normalized Difference Vegetation Index

**Formula:**
```
NDVI = (NIR - Red) / (NIR + Red)
```

**Algorithm:**
1. **DN Scaling Detection:**
   - If max(Red) > 1.0 or max(NIR) > 1.0 → DN-encoded
   - Apply scaling: value / 10000.0
   - Sentinel-2 L2A stores reflectance as 0–10000 range

2. **NDVI Calculation:**
   ```python
   numerator   = nir_band - red_band
   denominator = nir_band + red_band
   ndvi = numerator / denominator
   ```

3. **Division by Zero Handling:**
   - Where denominator = 0 → Set NDVI = NaN
   - Uses `np.where()` to avoid warnings

**Output:**
```
[NDVI] Computing NDVI …
[NDVI]  → Detected DN-encoded values (>1.0). Scaling bands by ÷ 10000.
[NDVI] ✓ NDVI computed.
```

**Returns:** NDVI array (float32) with values in range [-1, 1]

### 7. NDVI Statistics (`print_ndvi_statistics()`)

**Purpose:** Display NDVI summary metrics

**Metrics:**
- Minimum NDVI
- Maximum NDVI
- Mean NDVI
- Valid pixel count

**Output:**
```
──────────────────────────────────────────────────
  NDVI Statistics
──────────────────────────────────────────────────
  Min NDVI  : -0.1234
  Max NDVI  : 0.8456
  Mean NDVI : 0.6234
  Valid px  : 65234 / 65536
──────────────────────────────────────────────────
```

### 8. Output Saving (`save_outputs()`)

**Purpose:** Persist all output artifacts

**Files Generated:**

1. **red_band.tif** — Single-band GeoTIFF (B04)
2. **nir_band.tif** — Single-band GeoTIFF (B08)
3. **ndvi_map.png** — False-color visualization
4. **ndvi_raw.npy** — Raw NDVI NumPy array

**NDVI Visualization:**
- Colormap: `RdYlGn` (Red-Yellow-Green)
- Range: -1.0 to 1.0
- NaN pixels: Black
- DPI: 150
- Format: PNG

**Output:**
```
[SAVE] Writing output files …
[SAVE]  ✓ red_band.tif  → /path/to/red_band.tif
[SAVE]  ✓ nir_band.tif  → /path/to/nir_band.tif
[SAVE]  ✓ ndvi_map.png  → /path/to/ndvi_map.png
[SAVE]  ✓ ndvi_raw.npy  → /path/to/ndvi_raw.npy
[SAVE] ✓ All output files saved successfully.
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Configuration                                       │
│  • Load CLIENT_ID, CLIENT_SECRET                            │
│  • Set INPUT_MODE (bbox or center)                          │
│  • Define RESOLUTION, DAYS_BACK                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Authentication                                      │
│  • POST to TOKEN_URL with credentials                       │
│  • Receive access_token (valid 1 hour)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Bounding Box Resolution                            │
│  • Mode A: Use BBOX directly                                │
│  • Mode B: Generate from CENTER_LAT/LON + AREA_SIZE_KM      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Satellite Data Request                             │
│  • POST to PROCESS_URL with:                                │
│    - Bounding box                                            │
│    - Time range (last DAYS_BACK days)                       │
│    - Evalscript (fetch B04, B08)                            │
│  • Receive GeoTIFF bytes                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Band Extraction                                     │
│  • Load GeoTIFF with rasterio                               │
│  • Extract band 1 → red_band (B04)                          │
│  • Extract band 2 → nir_band (B08)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: Band Statistics                                     │
│  • Compute min, max, mean for B04                           │
│  • Compute min, max, mean for B08                           │
│  • Print to console                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 7: NDVI Computation                                    │
│  • Detect DN encoding (values > 1.0)                        │
│  • Scale if needed: bands / 10000.0                         │
│  • Calculate: (NIR - Red) / (NIR + Red)                     │
│  • Handle division by zero → NaN                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 8: NDVI Statistics                                     │
│  • Compute min, max, mean NDVI                              │
│  • Count valid pixels                                        │
│  • Print to console                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 9: Output Generation                                   │
│  • Save red_band.tif (GeoTIFF)                              │
│  • Save nir_band.tif (GeoTIFF)                              │
│  • Generate ndvi_map.png (visualization)                    │
│  • Save ndvi_raw.npy (NumPy array)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## NDVI Computation

### What is NDVI?

**NDVI (Normalized Difference Vegetation Index)** is a standardized measure of vegetation health derived from satellite imagery.

**Range:** -1.0 to +1.0

**Interpretation:**

| NDVI Range | Interpretation | Typical Features |
|------------|----------------|------------------|
| -1.0 to 0.0 | Water, clouds, snow | Non-vegetated |
| 0.0 to 0.2 | Bare soil, rock | Minimal vegetation |
| 0.2 to 0.4 | Sparse vegetation | Stressed crops, grassland |
| 0.4 to 0.6 | Moderate vegetation | Developing crops |
| 0.6 to 0.8 | Healthy vegetation | Mature, healthy crops |
| 0.8 to 1.0 | Dense vegetation | Peak greenness, forests |

### Formula Derivation

**Physical Basis:**
- Healthy vegetation reflects strongly in NIR (B08)
- Healthy vegetation absorbs strongly in Red (B04)
- Ratio captures this contrast

**Mathematical Form:**
```
NDVI = (NIR - Red) / (NIR + Red)
```

**Why Normalized?**
- Denominator normalizes for illumination differences
- Range [-1, 1] is consistent across scenes
- Reduces atmospheric effects

### DN Scaling

**Sentinel-2 L2A Encoding:**
- Reflectance stored as Digital Numbers (DN)
- Range: 0–10000 (represents 0.0–1.0 reflectance)
- Must divide by 10000 before NDVI calculation

**Detection Logic:**
```python
if np.nanmax(red_band) > 1.0 or np.nanmax(nir_band) > 1.0:
    red_band = red_band / 10000.0
    nir_band = nir_band / 10000.0
```

### Edge Cases

**Division by Zero:**
- Occurs when NIR + Red = 0 (rare)
- Handled by setting NDVI = NaN

**Cloud Pixels:**
- May have unusual reflectance values
- Appear as outliers in statistics
- Consider cloud masking for production

**Water Bodies:**
- Typically NDVI < 0
- NIR absorption by water
- Can be filtered if needed

---

## Usage Guide

### Basic Usage

1. **Configure credentials:**
```python
CLIENT_ID     = "your-client-id"
CLIENT_SECRET = "your-client-secret"
```

2. **Choose input mode:**
```python
# Option A: Bounding box
INPUT_MODE = "bbox"
BBOX = [77.50, 12.85, 77.70, 13.05]

# Option B: Center point
INPUT_MODE = "center"
CENTER_LAT   = 20.5937
CENTER_LON   = 78.9629
AREA_SIZE_KM = 10.0
```

3. **Run the script:**
```bash
cd "sentinel api testing"
python test_sentinel_ndvi.py
```

### Expected Output

```
==========================================================
 AgroSphere AI — Sentinel Hub Integration Test
==========================================================

[AUTH] Requesting access token …
[AUTH] ✓ Access token generated successfully.

[BBOX] Mode B: centre (20.5937, 78.9629), area 10.0 km
[BBOX] Generated bounding box: [78.9179, 20.5487, 79.0079, 20.6387]

[API] Sending satellite data request …
[API] Satellite API request status: 200
[API] ✓ Imagery data received.

[BANDS] Loading GeoTIFF …
[BANDS] ✓ GeoTIFF loaded successfully. Bands: 2, Size: 256×256
[BANDS] ✓ B04 (Red) and B08 (NIR) extracted.

──────────────────────────────────────────────────
  Band Statistics
──────────────────────────────────────────────────
  B04 (Red) → Min: 0.0234, Max: 0.1456, Mean: 0.0823
  B08 (NIR) → Min: 0.1123, Max: 0.4567, Mean: 0.2891
──────────────────────────────────────────────────

[NDVI] Computing NDVI …
[NDVI]  → Detected DN-encoded values (>1.0). Scaling bands by ÷ 10000.
[NDVI] ✓ NDVI computed.

──────────────────────────────────────────────────
  NDVI Statistics
──────────────────────────────────────────────────
  Min NDVI  : -0.1234
  Max NDVI  : 0.8456
  Mean NDVI : 0.6234
  Valid px  : 65234 / 65536
──────────────────────────────────────────────────

[SAVE] Writing output files …
[SAVE]  ✓ red_band.tif  → /path/to/red_band.tif
[SAVE]  ✓ nir_band.tif  → /path/to/nir_band.tif
[SAVE]  ✓ ndvi_map.png  → /path/to/ndvi_map.png
[SAVE]  ✓ ndvi_raw.npy  → /path/to/ndvi_raw.npy

[SAVE] ✓ All output files saved successfully.

Saved:
  - red_band.tif
  - nir_band.tif
  - ndvi_map.png
  - ndvi_raw.npy

==========================================================
 Test completed successfully.
==========================================================
```

### Advanced Configuration

**Higher Resolution:**
```python
RESOLUTION = 512  # or 1024 for high detail
```

**Longer Time Window:**
```python
DAYS_BACK = 60  # Look back 60 days
```

**Different Location:**
```python
# Example: Punjab wheat field
CENTER_LAT   = 30.9010
CENTER_LON   = 75.8573
AREA_SIZE_KM = 5.0
```

---

## Output Files

### 1. red_band.tif

**Format:** Single-band GeoTIFF  
**Content:** B04 (Red) reflectance values  
**Data Type:** Float32  
**CRS:** EPSG:4326 (WGS84)  
**Size:** 256×256 pixels (configurable)

**Usage:**
```python
import rasterio
with rasterio.open("red_band.tif") as src:
    red = src.read(1)
```

### 2. nir_band.tif

**Format:** Single-band GeoTIFF  
**Content:** B08 (NIR) reflectance values  
**Data Type:** Float32  
**CRS:** EPSG:4326 (WGS84)  
**Size:** 256×256 pixels (configurable)

**Usage:**
```python
import rasterio
with rasterio.open("nir_band.tif") as src:
    nir = src.read(1)
```

### 3. ndvi_map.png

**Format:** PNG image  
**Content:** False-color NDVI visualization  
**Colormap:** RdYlGn (Red-Yellow-Green)  
**Range:** -1.0 (red) to +1.0 (green)  
**NaN Pixels:** Black  
**DPI:** 150

**Interpretation:**
- Red areas: Low NDVI (stressed/bare)
- Yellow areas: Moderate NDVI
- Green areas: High NDVI (healthy vegetation)
- Black areas: No data (clouds, water)

### 4. ndvi_raw.npy

**Format:** NumPy binary array  
**Content:** Raw NDVI values  
**Data Type:** Float32  
**Shape:** (256, 256) or configured resolution

**Usage:**
```python
import numpy as np
ndvi = np.load("ndvi_raw.npy")
mean_ndvi = np.nanmean(ndvi)
print(f"Mean NDVI: {mean_ndvi:.4f}")
```

**Integration with Yield Engine:**
```python
# Extract mean NDVI for yield prediction
import numpy as np
from yield_engine.services.yield_calculator import YieldCalculator

ndvi = np.load("ndvi_raw.npy")
mean_ndvi = np.nanmean(ndvi)

calculator = YieldCalculator()
result = calculator.predict(
    region="punjab",
    crop="wheat",
    mean_ndvi=mean_ndvi
)
```

---

## API Reference

### Function: get_access_token()

```python
def get_access_token() -> str
```

**Purpose:** Authenticate with Sentinel Hub OAuth2

**Returns:** Bearer access token (string)

**Raises:**
- `requests.exceptions.HTTPError` — Authentication failed
- `ValueError` — No access_token in response

**Example:**
```python
token = get_access_token()
print(f"Token: {token[:20]}...")
```

### Function: generate_bbox_from_center()

```python
def generate_bbox_from_center(
    lat: float,
    lon: float,
    area_km: float
) -> list[float]
```

**Parameters:**
- `lat` — Center latitude (degrees)
- `lon` — Center longitude (degrees)
- `area_km` — Square side length (kilometers)

**Returns:** `[minLon, minLat, maxLon, maxLat]`

**Example:**
```python
bbox = generate_bbox_from_center(20.5937, 78.9629, 10.0)
# Returns: [78.9179, 20.5487, 79.0079, 20.6387]
```

### Function: fetch_satellite_data()

```python
def fetch_satellite_data(
    token: str,
    bbox: list[float]
) -> bytes
```

**Parameters:**
- `token` — Bearer access token
- `bbox` — Bounding box [minLon, minLat, maxLon, maxLat]

**Returns:** GeoTIFF bytes

**Raises:**
- `requests.exceptions.HTTPError` — API request failed

**Example:**
```python
tiff_bytes = fetch_satellite_data(token, bbox)
print(f"Received {len(tiff_bytes)} bytes")
```

### Function: extract_bands()

```python
def extract_bands(tiff_bytes: bytes) -> tuple[np.ndarray, np.ndarray]
```

**Parameters:**
- `tiff_bytes` — GeoTIFF binary data

**Returns:** `(red_band, nir_band)` as float32 arrays

**Example:**
```python
red, nir = extract_bands(tiff_bytes)
print(f"Red shape: {red.shape}")
print(f"NIR shape: {nir.shape}")
```

### Function: compute_ndvi()

```python
def compute_ndvi(
    red_band: np.ndarray,
    nir_band: np.ndarray
) -> np.ndarray
```

**Parameters:**
- `red_band` — B04 reflectance array
- `nir_band` — B08 reflectance array

**Returns:** NDVI array (float32, range [-1, 1])

**Example:**
```python
ndvi = compute_ndvi(red, nir)
mean_ndvi = np.nanmean(ndvi)
print(f"Mean NDVI: {mean_ndvi:.4f}")
```

### Function: print_band_statistics()

```python
def print_band_statistics(
    red_band: np.ndarray,
    nir_band: np.ndarray
) -> None
```

**Purpose:** Display band statistics to console

**Example:**
```python
print_band_statistics(red, nir)
```

### Function: print_ndvi_statistics()

```python
def print_ndvi_statistics(ndvi: np.ndarray) -> None
```

**Purpose:** Display NDVI statistics to console

**Example:**
```python
print_ndvi_statistics(ndvi)
```

### Function: save_outputs()

```python
def save_outputs(
    tiff_bytes: bytes,
    red_band: np.ndarray,
    nir_band: np.ndarray,
    ndvi: np.ndarray
) -> None
```

**Purpose:** Save all output files

**Generates:**
- red_band.tif
- nir_band.tif
- ndvi_map.png
- ndvi_raw.npy

**Example:**
```python
save_outputs(tiff_bytes, red, nir, ndvi)
```

---

## Troubleshooting

### Issue: "No 'access_token' field in response"

**Cause:** Invalid credentials

**Solution:**
1. Verify `CLIENT_ID` and `CLIENT_SECRET`
2. Check Sentinel Hub dashboard for correct values
3. Ensure OAuth client is active

### Issue: HTTP 401 Unauthorized

**Cause:** Authentication failed

**Solution:**
- Double-check credentials (no extra spaces)
- Verify account is active
- Check if OAuth client has required permissions

### Issue: HTTP 400 Bad Request

**Cause:** Invalid request payload

**Solution:**
- Verify bounding box coordinates are valid
- Check time range is not in the future
- Ensure resolution is reasonable (< 2500)

### Issue: HTTP 429 Too Many Requests

**Cause:** Rate limit exceeded

**Solution:**
- Wait before retrying
- Check Sentinel Hub plan limits
- Reduce request frequency

### Issue: "No valid (non-NaN) NDVI pixels found"

**Cause:** All pixels are clouds or water

**Solution:**
- Try different time window (increase `DAYS_BACK`)
- Choose different location
- Check if area is actually vegetated

### Issue: NDVI values all negative

**Cause:** Area is water body or urban

**Solution:**
- Verify coordinates point to agricultural land
- Check `ndvi_map.png` for visual confirmation

### Issue: "GeoTIFF loaded successfully" but bands are empty

**Cause:** No imagery available for time/location

**Solution:**
- Increase `DAYS_BACK` to 60 or 90
- Check Sentinel-2 coverage for your region
- Verify coordinates are correct

### Issue: DN scaling not applied (values > 1.0 in output)

**Cause:** Detection logic failed

**Solution:**
- Manually force scaling in `compute_ndvi()`
- Check if Sentinel Hub changed encoding

---

## Integration Notes

### Relationship with Yield Engine

**Current Architecture (Correct):**

```
┌──────────────────────────────────────┐
│  Sentinel API Testing Script         │
│  • Standalone validation tool        │
│  • Fetches imagery                   │
│  • Computes NDVI                     │
│  • Outputs: mean_ndvi scalar         │
└────────────────┬─────────────────────┘
                 │
                 │ mean_ndvi value
                 │
                 ▼
┌──────────────────────────────────────┐
│  Yield Prediction Engine              │
│  • Accepts mean_ndvi as input        │
│  • Does NOT fetch imagery            │
│  • Converts NDVI → yield prediction  │
└──────────────────────────────────────┘
```

**Key Principles:**
1. ✅ Sentinel script is standalone (testing only)
2. ✅ Yield engine accepts scalar `mean_ndvi`
3. ✅ No duplication of NDVI computation
4. ✅ Clean separation of concerns

### Future Integration Path

When ready to integrate into production:

**Option 1: Extract mean_ndvi manually**
```bash
# Run Sentinel script
python test_sentinel_ndvi.py
# Note mean NDVI from output

# Use in yield engine
python yield-engine/main.py
# Pass mean_ndvi as parameter
```

**Option 2: Create bridge module**
```python
# yield-engine/services/satellite_bridge.py
from sentinel_testing import (
    get_access_token,
    fetch_satellite_data,
    extract_bands,
    compute_ndvi
)

def fetch_mean_ndvi(lat, lon, area_km):
    """Fetch imagery and return mean NDVI scalar"""
    token = get_access_token()
    bbox = generate_bbox_from_center(lat, lon, area_km)
    tiff_bytes = fetch_satellite_data(token, bbox)
    red, nir = extract_bands(tiff_bytes)
    ndvi = compute_ndvi(red, nir)
    return np.nanmean(ndvi)
```

**Option 3: FastAPI endpoint**
```python
# Backend/app/routers/satellite.py
@router.post("/fetch-ndvi")
async def fetch_ndvi(lat: float, lon: float, area_km: float):
    """Fetch NDVI for given location"""
    # Use Sentinel logic here
    mean_ndvi = fetch_mean_ndvi(lat, lon, area_km)
    return {"mean_ndvi": mean_ndvi}
```

### Security Considerations

⚠️ **Never commit credentials to Git:**
```bash
# Add to .gitignore
sentinel api testing/.env
sentinel api testing/credentials.py
```

✅ **Use environment variables in production:**
```python
import os
CLIENT_ID = os.getenv("SENTINEL_CLIENT_ID")
CLIENT_SECRET = os.getenv("SENTINEL_CLIENT_SECRET")
```

✅ **Use .env file for local development:**
```bash
# .env
SENTINEL_CLIENT_ID=your-client-id
SENTINEL_CLIENT_SECRET=your-client-secret
```

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Appendix: Sentinel-2 Bands

### Band Overview

| Band | Name | Wavelength (nm) | Resolution (m) | Purpose |
|------|------|-----------------|----------------|---------|
| B01 | Coastal aerosol | 443 | 60 | Atmospheric correction |
| B02 | Blue | 490 | 10 | True color, water |
| B03 | Green | 560 | 10 | True color, vegetation |
| B04 | Red | 665 | 10 | Vegetation, NDVI |
| B05 | Red Edge 1 | 705 | 20 | Vegetation stress |
| B06 | Red Edge 2 | 740 | 20 | Vegetation stress |
| B07 | Red Edge 3 | 783 | 20 | Vegetation stress |
| B08 | NIR | 842 | 10 | Vegetation, NDVI |
| B8A | Narrow NIR | 865 | 20 | Water vapor |
| B09 | Water vapor | 945 | 60 | Atmospheric |
| B10 | SWIR Cirrus | 1375 | 60 | Cloud detection |
| B11 | SWIR 1 | 1610 | 20 | Moisture, fire |
| B12 | SWIR 2 | 2190 | 20 | Moisture, geology |

### Bands Used in This Script

**B04 (Red):**
- Wavelength: 665 nm
- Resolution: 10m
- Absorbed by chlorophyll
- Low reflectance in healthy vegetation

**B08 (NIR):**
- Wavelength: 842 nm
- Resolution: 10m
- Reflected by leaf structure
- High reflectance in healthy vegetation

---

## Appendix: NDVI Alternatives

### Other Vegetation Indices

**EVI (Enhanced Vegetation Index):**
```
EVI = 2.5 × (NIR - Red) / (NIR + 6×Red - 7.5×Blue + 1)
```
- Better in high biomass areas
- Reduces atmospheric effects

**SAVI (Soil-Adjusted Vegetation Index):**
```
SAVI = (NIR - Red) / (NIR + Red + L) × (1 + L)
```
- L = 0.5 (soil brightness correction)
- Better for sparse vegetation

**NDWI (Normalized Difference Water Index):**
```
NDWI = (Green - NIR) / (Green + NIR)
```
- Detects water content
- Useful for irrigation monitoring

### Why NDVI?

✅ Simple and robust  
✅ Well-established in agriculture  
✅ Requires only 2 bands (B04, B08)  
✅ Directly correlates with biomass  
✅ Widely used in research and industry

---

**End of Documentation**

*Last updated: February 22, 2026*  
*AgroSphere AI — Sentinel Hub API Integration v1.0.0*
