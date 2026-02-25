# Simple Guide - Share Sensor Data with Your Friend

## Step 1: Edit the Script

Open `sensor_to_backend.py` and change line 22:

```python
BACKEND_URL = "http://YOUR_FRIEND_BACKEND_IP:PORT/api/sensor-data"
```

Example:
```python
BACKEND_URL = "http://192.168.1.100:5000/api/sensor-data"
```

## Step 2: Install requests library

On Raspberry Pi:
```bash
pip3 install --break-system-packages requests
```

## Step 3: Run the script

```bash
cd ~/agrosphere-iot
python3 sensor_to_backend.py
```

## What it does:

1. Reads DHT11 (temperature, humidity) every 2 seconds
2. Reads Soil Moisture every 2 seconds
3. Prints JSON to console
4. POSTs JSON to your friend's backend
5. Shows success/error count

## Your friend's backend should expect:

```json
{
  "timestamp": "2026-02-25T00:30:00.123456",
  "node_id": "agrosphere_edge_001",
  "temperature_celsius": 28.9,
  "humidity_percent": 42.0,
  "soil_moisture_percent": 0.0,
  "market_warning": true,
  "status": "CRITICAL"
}
```

That's it! Simple and works!
