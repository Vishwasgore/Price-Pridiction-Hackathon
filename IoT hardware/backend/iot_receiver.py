#!/usr/bin/env python3
"""
AgroSphere AI - IoT Data Receiver Backend
==========================================
Simple Flask server to receive real-time sensor data from Raspberry Pi.
Run this on your Windows machine or any server.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Store latest sensor data in memory
latest_data = {}
data_history = []
MAX_HISTORY = 100

@app.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    """Receive sensor data from Raspberry Pi"""
    try:
        data = request.get_json()
        
        # Store latest data
        global latest_data
        latest_data = data
        
        # Add to history
        data_history.append(data)
        if len(data_history) > MAX_HISTORY:
            data_history.pop(0)
        
        # Print to console
        print("=" * 70)
        print(f"📡 Received at {datetime.now().strftime('%H:%M:%S')}")
        print(json.dumps(data, indent=2))
        
        # Check for warnings
        if data.get('market_warning'):
            print("⚠️  MARKET WARNING DETECTED!")
            print(f"   Status: {data.get('status')}")
        
        print("=" * 70)
        print()
        
        return jsonify({
            "status": "success",
            "message": "Data received",
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@app.route('/api/sensor-data', methods=['GET'])
def get_latest_data():
    """Get latest sensor data"""
    if latest_data:
        return jsonify(latest_data), 200
    else:
        return jsonify({
            "status": "no_data",
            "message": "No data received yet"
        }), 404


@app.route('/api/sensor-history', methods=['GET'])
def get_history():
    """Get sensor data history"""
    return jsonify({
        "count": len(data_history),
        "data": data_history
    }), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AgroSphere IoT Receiver",
        "timestamp": datetime.now().isoformat(),
        "data_received": len(data_history)
    }), 200


@app.route('/')
def index():
    """Simple dashboard"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AgroSphere AI - IoT Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
            }
            .card {
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .value {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }
            .warning {
                background: #fee;
                border-left: 4px solid #f00;
                padding: 15px;
                margin: 10px 0;
            }
            .normal {
                background: #efe;
                border-left: 4px solid #0f0;
                padding: 15px;
                margin: 10px 0;
            }
            pre {
                background: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
        </style>
        <script>
            function refreshData() {
                fetch('/api/sensor-data')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('data').textContent = JSON.stringify(data, null, 2);
                        document.getElementById('temp').textContent = data.temperature_celsius + '°C';
                        document.getElementById('humidity').textContent = data.humidity_percent + '%';
                        document.getElementById('moisture').textContent = data.soil_moisture_percent + '%';
                        document.getElementById('status').textContent = data.status;
                        document.getElementById('status').className = data.market_warning ? 'warning' : 'normal';
                    })
                    .catch(e => {
                        document.getElementById('data').textContent = 'No data received yet';
                    });
            }
            
            setInterval(refreshData, 2000);
            refreshData();
        </script>
    </head>
    <body>
        <div class="header">
            <h1>🌾 AgroSphere AI</h1>
            <p>Real-Time IoT Data Receiver</p>
        </div>
        
        <div class="card">
            <h2>Latest Sensor Data</h2>
            <p><strong>Temperature:</strong> <span class="value" id="temp">--</span></p>
            <p><strong>Humidity:</strong> <span class="value" id="humidity">--</span></p>
            <p><strong>Soil Moisture:</strong> <span class="value" id="moisture">--</span></p>
            <div id="status" class="normal">Loading...</div>
        </div>
        
        <div class="card">
            <h2>Raw JSON Data</h2>
            <pre id="data">Waiting for data...</pre>
        </div>
    </body>
    </html>
    """
    return html


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 AgroSphere AI - IoT Data Receiver")
    print("=" * 70)
    print("Server starting on http://0.0.0.0:5000")
    print("Dashboard: http://localhost:5000")
    print("API Endpoint: http://localhost:5000/api/sensor-data")
    print("=" * 70)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
