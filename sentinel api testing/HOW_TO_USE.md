# How to Test Sentinel API with Your Coordinates

## Quick Start (3 Simple Steps)

### Step 1: Edit Coordinates
Open `coordinates.py` and update these three values:

```python
CENTER_LAT   = 25.385152    # Your latitude
CENTER_LON   = 95.585753    # Your longitude
AREA_SIZE_KM = 10.0         # Area size in km
```

### Step 2: Run the Script
```bash
python test_sentinel_ndvi.py
```

### Step 3: Check Results
Look at the generated files:
- `ndvi_map.png` - Visual map of vegetation
- `ndvi_raw.npy` - Raw NDVI data
- `red_band.tif` - Red band imagery
- `nir_band.tif` - NIR band imagery

---

## Example Coordinates

### Delhi, India
```python
CENTER_LAT   = 28.6139
CENTER_LON   = 77.2090
AREA_SIZE_KM = 10.0
```

### Mumbai, India
```python
CENTER_LAT   = 19.0760
CENTER_LON   = 72.8777
AREA_SIZE_KM = 10.0
```

### Punjab (Agricultural)
```python
CENTER_LAT   = 30.9010
CENTER_LON   = 75.8573
AREA_SIZE_KM = 10.0
```

---

## Understanding NDVI Results

| Mean NDVI | Interpretation |
|-----------|----------------|
| < 0.2 | Bare soil, desert, urban |
| 0.2 - 0.4 | Sparse vegetation, stressed crops |
| 0.4 - 0.6 | Moderate vegetation |
| 0.6 - 0.8 | Healthy crops, grassland |
| > 0.8 | Dense forest, peak vegetation |

---

## Files Structure

```
sentinel api testing/
├── coordinates.py              ← EDIT THIS FILE
├── test_sentinel_ndvi.py       ← RUN THIS FILE
├── HOW_TO_USE.md              ← This guide
├── SENTINEL_API_DOCUMENTATION.md
└── Output files (generated):
    ├── ndvi_map.png
    ├── ndvi_raw.npy
    ├── red_band.tif
    └── nir_band.tif
```

---

## That's It!

No need to touch the main script. Just edit `coordinates.py` and run!
