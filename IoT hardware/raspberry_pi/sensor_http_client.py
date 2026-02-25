#!/usr/bin/env python3
"""
AgroSphere AI - HTTP Client for Backend Integration
====================================================
Sends real-time sensor data to your backend API via HTTP POST.
Configure your backend endpoint below.

Usage:
    python3 sensor_http_client.py
"""

import asyncio
import json
from collections import deque
from datetime import datetime
from typing import Dict, Optional, Tuple
import aiohttp

import board
import adafruit_dht
import RPi.GPIO as GPIO

# ============================================================================
# CONFIGURATION
# ============================================================================

# CONFIGURE YOUR BACKEND API ENDPOINT HERE
BACKEND_API_URL = "http://YOUR_BACKEND_IP:PORT/api/sensor-data"
API_KEY = "your_api_key_here"  # Optional: Add authentication

DHT11_PIN = board.D27
SOIL_MOISTURE_PIN = 17

TEMP_THRESHOLD = 35.0
MOISTURE_THRESHOLD = 20.0

DHT11_RETRY_ATTEMPTS = 3
DHT11_RETRY_DELAY = 2.0
SEND_INTERVAL = 2.0  # Send to backend every 2 seconds

WINDOW_SIZE = 5

# ============================================================================
# MOVING AVERAGE FILTER
# ============================================================================

class MovingAverage:
    def __init__(self, size: int = 5):
        self.buffer = deque(maxlen=size)
    
    def add(self, value: float) -> float:
        self.buffer.append(value)
        return sum(self.buffer) / len(self.buffer)


# ============================================================================
# SENSOR READERS (Same as WebSocket version)
# ============================================================================

class DHT11Sensor:
    def __init__(self, pin):
        self.device = adafruit_dht.DHT11(pin)
        self.temp_filter = MovingAverage(WINDOW_SIZE)
        self.humidity_filter = MovingAverage(WINDOW_SIZE)
        self.error_count = 0
        self.read_count = 0
        self.last_temp = None
        self.last_humidity = None
    
    async def read(self) -> Tuple[Optional[float], Optional[float], float]:
        self.read_count += 1
        
        for attempt in range(DHT11_RETRY_ATTEMPTS):
            try:
                temp = self.device.temperature
                humidity = self.device.humidity
                
                if temp is not None and humidity is not None:
                    smoothed_temp = self.temp_filter.add(temp)
                    smoothed_humidity = self.humidity_filter.add(humidity)
                    
                    self.last_temp = smoothed_temp
                    self.last_humidity = smoothed_humidity
                    
                    confidence = 1.0 - (self.error_count / max(self.read_count, 1))
                    return smoothed_temp, smoothed_humidity, max(0.0, min(1.0, confidence))
                
            except RuntimeError:
                if attempt < DHT11_RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(DHT11_RETRY_DELAY)
                else:
                    self.error_count += 1
            except Exception:
                self.error_count += 1
                break
        
        confidence = max(0.0, 1.0 - (self.error_count / max(self.read_count, 1)))
        return self.last_temp, self.last_humidity, confidence
    
    def cleanup(self):
        self.device.exit()


class SoilMoistureSensor:
    def __init__(self, pin: int):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)
        self.filter = MovingAverage(WINDOW_SIZE)
    
    async def read(self) -> Optional[float]:
        try:
            digital = GPIO.input(self.pin)
            moisture = 100.0 if digital == 0 else 0.0
            return self.filter.add(moisture)
        except Exception:
            return None
    
    @staticmethod
    def cleanup():
        GPIO.cleanup()


# ============================================================================
# HTTP CLIENT
# ============================================================================

class HTTPSensorClient:
    def __init__(self):
        self.dht = DHT11Sensor(DHT11_PIN)
        self.soil = SoilMoistureSensor(SOIL_MOISTURE_PIN)
        self.session = None
        self.success_count = 0
        self.error_count = 0
    
    async def send_to_backend(self, data: Dict) -> bool:
        """Send data to backend API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            }
            
            async with self.session.post(
                BACKEND_API_URL,
                json=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    self.success_count += 1
                    return True
                else:
                    self.error_count += 1
                    print(f"❌ Backend error: {response.status}")
                    return False
                    
        except aiohttp.ClientError as e:
            self.error_count += 1
            print(f"❌ Connection error: {e}")
            return False
        except Exception as e:
            self.error_count += 1
            print(f"❌ Unexpected error: {e}")
            return False
    
    async def run(self):
        """Main loop"""
        print("=" * 70)
        print("AgroSphere AI - HTTP Backend Client")
        print("=" * 70)
        print(f"Backend API: {BACKEND_API_URL}")
        print(f"Send Interval: {SEND_INTERVAL}s")
        print("=" * 70)
        print()
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            while True:
                # Read sensors
                temp, humidity, confidence = await self.dht.read()
                moisture = await self.soil.read()
                
                if temp is not None and humidity is not None and moisture is not None:
                    market_warning = (temp > TEMP_THRESHOLD) or (moisture < MOISTURE_THRESHOLD)
                    
                    data = {
                        "timestamp": datetime.now().isoformat(),
                        "node_id": "agrosphere_edge_001",
                        "sensor_data": {
                            "temperature_celsius": round(temp, 2),
                            "humidity_percent": round(humidity, 2),
                            "soil_moisture_percent": round(moisture, 2)
                        },
                        "confidence_score": round(confidence, 3),
                        "market_warning": market_warning,
                        "status": "CRITICAL" if market_warning else "NORMAL"
                    }
                    
                    # Send to backend
                    success = await self.send_to_backend(data)
                    
                    status = "✅" if success else "❌"
                    print(f"{status} Temp: {temp:.1f}°C | Moisture: {moisture:.1f}% | Success: {self.success_count} | Errors: {self.error_count}")
                
                await asyncio.sleep(SEND_INTERVAL)
    
    def cleanup(self):
        self.dht.cleanup()
        self.soil.cleanup()


# ============================================================================
# MAIN
# ============================================================================

async def main():
    client = HTTPSensorClient()
    try:
        await client.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down client...")
    finally:
        client.cleanup()
        print("✅ Cleanup complete")


if __name__ == "__main__":
    asyncio.run(main())
