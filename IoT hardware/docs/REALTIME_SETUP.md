# Real-Time Sensor Streaming Setup

## Option 1: WebSocket Server (Recommended)

### On Raspberry Pi:
```bash
# Install dependencies
pip3 install websockets aiohttp

# Run WebSocket server
python3 sensor_websocket_server.py
```

Server runs on: `ws://YOUR_RPI_IP:8765`

### Test with HTML Client:
Open `websocket_test_client.html` in your browser and connect!

### Connect from Your Backend:
```python
import websockets
import asyncio

async def connect():
    async with websockets.connect('ws://192.168.1.18:8765') as ws:
        async for message in ws:
            data = json.loads(message)
            print(data)
```

## Option 2: HTTP POST to Backend

Edit `sensor_http_client.py` and set:
```python
BACKEND_API_URL = "http://your-backend.com/api/sensor-data"
```

Then run:
```bash
python3 sensor_http_client.py
```
