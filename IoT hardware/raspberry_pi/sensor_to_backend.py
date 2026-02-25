#!/usr/bin/env python3
"""
AgroSphere AI - Send Sensor Data to Backend in Real-Time
=========================================================
Simple script that reads sensors and POSTs to your friend's backend API.
"""

import asyncio
import json
from collections import deque
from datetime import datetime
from typing import Optional, Tuple
import requests  # Using requests instead of aiohttp for simplicity

import board
import adafruit_dht
import RPi.GPIO as GPIO

# ============================================================================
# CONFIGURE YOUR FRIEND'S BACKEND HERE
# ============================================================================
BACKEND_URL = "https://mamie-prognosticable-chadwick.ngrok-free.dev/api/sensor-data"

# ============================================================================
# CONFIGURATION
# ============================================================================
DHT11_PIN = board.D27
SOIL_MOISTURE_PIN = 17
SEND_INTERVAL = 2  # Send data every 2 seconds
WINDOW_SIZE = 5

# ============================================================================
# MOVING AVERAGE
# ============================================================================
class MovingAverage:
    def __init__(self, size=5):
        self.buffer = deque(maxlen=size)
    
    def add(self, value):
        self.buffer.append(value)
        return sum(self.buffer) / len(self.buffer)

# ============================================================================
# SENSORS
# ============================================================================
class DHT11Sensor:
    def __init__(self, pin):
        self.device = adafruit_dht.DHT11(pin)
        self.temp_filter = MovingAverage(WINDOW_SIZE)
        self.humidity_filter = MovingAverage(WINDOW_SIZE)
        self.last_temp = None
        self.last_humidity = None
    
    async def read(self):
        for attempt in range(3):
            try:
                temp = self.device.temperature
                humidity = self.device.humidity
                
                if temp is not None and humidity is not None:
                    self.last_temp = self.temp_filter.add(temp)
                    self.last_humidity = self.humidity_filter.add(humidity)
                    return self.last_temp, self.last_humidity
            except RuntimeError:
                await asyncio.sleep(2)
        
        return self.last_temp, self.last_humidity
    
    def cleanup(self):
        self.device.exit()

class SoilMoistureSensor:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)
        self.filter = MovingAverage(WINDOW_SIZE)
    
    async def read(self):
        try:
            digital = GPIO.input(self.pin)
            moisture = 100.0 if digital == 0 else 0.0
            return self.filter.add(moisture)
        except:
            return None
    
    @staticmethod
    def cleanup():
        GPIO.cleanup()

# ============================================================================
# MAIN
# ============================================================================
async def main():
    print("=" * 70)
    print("AgroSphere AI - Real-Time Backend Integration")
    print("=" * 70)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Send Interval: {SEND_INTERVAL}s")
    print("=" * 70)
    print()
    
    dht = DHT11Sensor(DHT11_PIN)
    soil = SoilMoistureSensor(SOIL_MOISTURE_PIN)
    
    success_count = 0
    error_count = 0
    
    try:
        while True:
            # Read sensors
            temp, humidity = await dht.read()
            moisture = await soil.read()
            
            if temp and humidity and moisture is not None:
                # Prepare data
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "node_id": "agrosphere_edge_001",
                    "temperature_celsius": round(temp, 2),
                    "humidity_percent": round(humidity, 2),
                    "soil_moisture_percent": round(moisture, 2),
                    "market_warning": temp > 35 or moisture < 20,
                    "status": "CRITICAL" if (temp > 35 or moisture < 20) else "NORMAL"
                }
                
                # Print to console
                print(json.dumps(data, indent=2))
                
                # Send to backend
                try:
                    response = requests.post(
                        BACKEND_URL,
                        json=data,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        success_count += 1
                        print(f"✅ Sent to backend | Success: {success_count} | Errors: {error_count}")
                    else:
                        error_count += 1
                        print(f"❌ Backend error {response.status_code} | Success: {success_count} | Errors: {error_count}")
                
                except requests.exceptions.RequestException as e:
                    error_count += 1
                    print(f"❌ Connection failed: {e}")
                    print(f"   Success: {success_count} | Errors: {error_count}")
                
                print()
            
            await asyncio.sleep(SEND_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        dht.cleanup()
        soil.cleanup()
        print("✅ Cleanup complete")

if __name__ == "__main__":
    asyncio.run(main())
