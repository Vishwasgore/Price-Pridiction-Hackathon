# AgroSphere AI - API Integration Guide

## 🌐 Your Public API Endpoint

```
https://mamie-prognosticable-chadwick.ngrok-free.dev
```

## 📡 Available Endpoints

### 1. Get Latest Sensor Data
```
GET https://mamie-prognosticable-chadwick.ngrok-free.dev/api/sensor-data
```

**Response:**
```json
{
  "timestamp": "2026-02-25T10:35:00.899954",
  "node_id": "agrosphere_edge_001",
  "temperature_celsius": 29.17,
  "humidity_percent": 36.33,
  "soil_moisture_percent": 0.0,
  "market_warning": true,
  "status": "CRITICAL"
}
```

### 2. Get Historical Data (Last 100 readings)
```
GET https://mamie-prognosticable-chadwick.ngrok-free.dev/api/sensor-history
```

**Response:**
```json
{
  "count": 100,
  "data": [
    {
      "timestamp": "2026-02-25T10:35:00.899954",
      "temperature_celsius": 29.17,
      ...
    },
    ...
  ]
}
```

### 3. Health Check
```
GET https://mamie-prognosticable-chadwick.ngrok-free.dev/api/health
```

### 4. Dashboard (HTML)
```
GET https://mamie-prognosticable-chadwick.ngrok-free.dev/
```

---

## 💻 Integration Examples

### Python Integration

```python
import requests
import time

# Configuration
API_BASE_URL = "https://mamie-prognosticable-chadwick.ngrok-free.dev"

def get_latest_sensor_data():
    """Get the latest sensor reading"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/sensor-data")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def get_sensor_history():
    """Get historical sensor data"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/sensor-history")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def monitor_sensors_realtime():
    """Monitor sensors in real-time"""
    print("Starting real-time monitoring...")
    while True:
        data = get_latest_sensor_data()
        if data:
            print(f"\n{'='*50}")
            print(f"Timestamp: {data['timestamp']}")
            print(f"Temperature: {data['temperature_celsius']}°C")
            print(f"Humidity: {data['humidity_percent']}%")
            print(f"Soil Moisture: {data['soil_moisture_percent']}%")
            print(f"Status: {data['status']}")
            
            if data['market_warning']:
                print("⚠️  MARKET WARNING ACTIVE!")
        
        time.sleep(5)  # Poll every 5 seconds

# Example usage
if __name__ == "__main__":
    # Get latest data
    latest = get_latest_sensor_data()
    print("Latest Data:", latest)
    
    # Get history
    history = get_sensor_history()
    print(f"Historical Records: {history['count']}")
    
    # Start real-time monitoring
    # monitor_sensors_realtime()
```

---

### JavaScript/Node.js Integration

```javascript
const axios = require('axios');

const API_BASE_URL = 'https://mamie-prognosticable-chadwick.ngrok-free.dev';

// Get latest sensor data
async function getLatestSensorData() {
    try {
        const response = await axios.get(`${API_BASE_URL}/api/sensor-data`);
        return response.data;
    } catch (error) {
        console.error('Error fetching data:', error.message);
        return null;
    }
}

// Get sensor history
async function getSensorHistory() {
    try {
        const response = await axios.get(`${API_BASE_URL}/api/sensor-history`);
        return response.data;
    } catch (error) {
        console.error('Error fetching history:', error.message);
        return null;
    }
}

// Real-time monitoring
async function monitorSensorsRealtime() {
    console.log('Starting real-time monitoring...');
    
    setInterval(async () => {
        const data = await getLatestSensorData();
        
        if (data) {
            console.log('\n' + '='.repeat(50));
            console.log(`Timestamp: ${data.timestamp}`);
            console.log(`Temperature: ${data.temperature_celsius}°C`);
            console.log(`Humidity: ${data.humidity_percent}%`);
            console.log(`Soil Moisture: ${data.soil_moisture_percent}%`);
            console.log(`Status: ${data.status}`);
            
            if (data.market_warning) {
                console.log('⚠️  MARKET WARNING ACTIVE!');
            }
        }
    }, 5000); // Poll every 5 seconds
}

// Example usage
(async () => {
    // Get latest data
    const latest = await getLatestSensorData();
    console.log('Latest Data:', latest);
    
    // Get history
    const history = await getSensorHistory();
    console.log(`Historical Records: ${history.count}`);
    
    // Start monitoring
    // monitorSensorsRealtime();
})();
```

---

### React Integration (Frontend)

```javascript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'https://mamie-prognosticable-chadwick.ngrok-free.dev';

function SensorDashboard() {
    const [sensorData, setSensorData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch data every 5 seconds
        const fetchData = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/api/sensor-data`);
                setSensorData(response.data);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching sensor data:', error);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);

        return () => clearInterval(interval);
    }, []);

    if (loading) return <div>Loading...</div>;

    return (
        <div className="sensor-dashboard">
            <h1>AgroSphere AI - Live Sensor Data</h1>
            
            <div className="sensor-cards">
                <div className="card">
                    <h3>Temperature</h3>
                    <p className="value">{sensorData.temperature_celsius}°C</p>
                </div>
                
                <div className="card">
                    <h3>Humidity</h3>
                    <p className="value">{sensorData.humidity_percent}%</p>
                </div>
                
                <div className="card">
                    <h3>Soil Moisture</h3>
                    <p className="value">{sensorData.soil_moisture_percent}%</p>
                </div>
            </div>
            
            {sensorData.market_warning && (
                <div className="alert">
                    ⚠️ Market Warning: {sensorData.status}
                </div>
            )}
            
            <p className="timestamp">
                Last updated: {new Date(sensorData.timestamp).toLocaleString()}
            </p>
        </div>
    );
}

export default SensorDashboard;
```

---

### cURL (Command Line)

```bash
# Get latest data
curl https://mamie-prognosticable-chadwick.ngrok-free.dev/api/sensor-data

# Get history
curl https://mamie-prognosticable-chadwick.ngrok-free.dev/api/sensor-history

# Pretty print with jq
curl -s https://mamie-prognosticable-chadwick.ngrok-free.dev/api/sensor-data | jq .
```

---

### PHP Integration

```php
<?php

$API_BASE_URL = 'https://mamie-prognosticable-chadwick.ngrok-free.dev';

function getLatestSensorData() {
    global $API_BASE_URL;
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "$API_BASE_URL/api/sensor-data");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    curl_close($ch);
    
    return json_decode($response, true);
}

function getSensorHistory() {
    global $API_BASE_URL;
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "$API_BASE_URL/api/sensor-history");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    curl_close($ch);
    
    return json_decode($response, true);
}

// Example usage
$latest = getLatestSensorData();
echo "Temperature: " . $latest['temperature_celsius'] . "°C\n";
echo "Humidity: " . $latest['humidity_percent'] . "%\n";
echo "Status: " . $latest['status'] . "\n";

?>
```

---

## 🔄 WebSocket Alternative (Real-time Streaming)

If you need true real-time streaming without polling, you can use the WebSocket server:

```python
import asyncio
import websockets
import json

async def connect_to_sensors():
    uri = "ws://192.168.1.18:8765"  # Use this if on same network
    
    async with websockets.connect(uri) as websocket:
        print("Connected to sensor stream!")
        
        async for message in websocket:
            data = json.loads(message)
            
            if data['type'] == 'sensor_data':
                print(f"Temp: {data['sensor_data']['temperature_celsius']}°C")
                print(f"Moisture: {data['sensor_data']['soil_moisture_percent']}%")
                print(f"Status: {data['status']}")

asyncio.run(connect_to_sensors())
```

---

## 🎯 Use Cases

### 1. Price Prediction Service
```python
def adjust_price_prediction(sensor_data):
    """Adjust crop price based on sensor data"""
    base_price = 100
    
    # Heat stress reduces yield
    if sensor_data['temperature_celsius'] > 35:
        base_price *= 1.15  # Price increases due to reduced supply
    
    # Drought stress impacts quality
    if sensor_data['soil_moisture_percent'] < 20:
        base_price *= 1.10  # Price increases
    
    return base_price
```

### 2. Alert System
```python
def check_alerts(sensor_data):
    """Send alerts based on sensor thresholds"""
    alerts = []
    
    if sensor_data['market_warning']:
        alerts.append({
            'type': 'MARKET_WARNING',
            'message': f"Critical conditions detected: {sensor_data['status']}",
            'action': 'Consider early harvest or sale'
        })
    
    return alerts
```

### 3. Data Analytics
```python
def analyze_trends(history_data):
    """Analyze sensor trends over time"""
    temps = [d['temperature_celsius'] for d in history_data['data']]
    avg_temp = sum(temps) / len(temps)
    
    return {
        'average_temperature': avg_temp,
        'trend': 'increasing' if temps[-1] > avg_temp else 'decreasing'
    }
```

---

## 📊 Database Integration

### Store in PostgreSQL
```python
import psycopg2
import requests

def store_sensor_data_in_db():
    # Get data from API
    data = requests.get(f"{API_BASE_URL}/api/sensor-data").json()
    
    # Connect to database
    conn = psycopg2.connect(
        host="localhost",
        database="agrosphere",
        user="your_user",
        password="your_password"
    )
    
    cursor = conn.cursor()
    
    # Insert data
    cursor.execute("""
        INSERT INTO sensor_readings 
        (timestamp, node_id, temperature, humidity, soil_moisture, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['timestamp'],
        data['node_id'],
        data['temperature_celsius'],
        data['humidity_percent'],
        data['soil_moisture_percent'],
        data['status']
    ))
    
    conn.commit()
    cursor.close()
    conn.close()
```

---

## 🔐 Security Considerations

1. **API Key Authentication** (Optional)
   - Add authentication to your Flask backend
   - Require API keys for access

2. **Rate Limiting**
   - Implement rate limiting to prevent abuse
   - Use libraries like `flask-limiter`

3. **HTTPS Only**
   - ngrok provides HTTPS by default
   - Always use HTTPS in production

---

## 📝 Notes

- **ngrok URL changes** when you restart ngrok (free tier)
- **Update your services** with new URL after restart
- **For production:** Use paid ngrok or deploy to cloud (AWS, Heroku, etc.)
- **Data updates:** Every 2 seconds from Raspberry Pi
- **History limit:** Last 100 readings stored in memory

---

## 🆘 Troubleshooting

**Problem:** API returns 404
- Check ngrok is running
- Verify URL is correct

**Problem:** No data returned
- Check Raspberry Pi script is running
- Verify Flask backend is running

**Problem:** Stale data
- Raspberry Pi may have disconnected
- Check network connection
