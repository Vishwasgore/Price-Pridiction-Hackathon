#!/usr/bin/env python3
"""
AgroSphere AI - Real-Time IoT WebSocket Server
===============================================
Streams sensor data in real-time via WebSocket for integration with
backend services, dashboards, and price prediction models.

Usage:
    python3 sensor_websocket_server.py
    
Connect from client:
    ws://RASPBERRY_PI_IP:8765
"""

import asyncio
import json
from collections import deque
from datetime import datetime
from typing import Dict, Optional, Set, Tuple
import websockets

import board
import adafruit_dht
import RPi.GPIO as GPIO

# ============================================================================
# CONFIGURATION
# ============================================================================

WEBSOCKET_HOST = "0.0.0.0"  # Listen on all interfaces
WEBSOCKET_PORT = 8765

DHT11_PIN = board.D27
SOIL_MOISTURE_PIN = 17

TEMP_THRESHOLD = 35.0
MOISTURE_THRESHOLD = 20.0

DHT11_RETRY_ATTEMPTS = 3
DHT11_RETRY_DELAY = 2.0
BROADCAST_INTERVAL = 2.0  # Send data every 2 seconds

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
    
    def get(self) -> Optional[float]:
        return sum(self.buffer) / len(self.buffer) if self.buffer else None


# ============================================================================
# SENSOR READERS
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
                    confidence = max(0.0, min(1.0, confidence))
                    
                    return smoothed_temp, smoothed_humidity, confidence
                
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
            smoothed = self.filter.add(moisture)
            return smoothed
        except Exception:
            return None
    
    @staticmethod
    def cleanup():
        GPIO.cleanup()


# ============================================================================
# WEBSOCKET SERVER
# ============================================================================

class SensorWebSocketServer:
    def __init__(self):
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.dht = DHT11Sensor(DHT11_PIN)
        self.soil = SoilMoistureSensor(SOIL_MOISTURE_PIN)
        self.shared_data = {
            'temperature': None,
            'humidity': None,
            'moisture': None,
            'confidence': 0.0
        }
    
    async def register_client(self, websocket):
        """Register new WebSocket client"""
        self.clients.add(websocket)
        print(f"✅ Client connected: {websocket.remote_address} | Total: {len(self.clients)}")
        
        # Send welcome message
        welcome = {
            "type": "connection",
            "status": "connected",
            "message": "AgroSphere AI - Real-Time Sensor Stream",
            "node_id": "agrosphere_edge_001"
        }
        await websocket.send(json.dumps(welcome))
    
    async def unregister_client(self, websocket):
        """Unregister disconnected client"""
        self.clients.remove(websocket)
        print(f"❌ Client disconnected: {websocket.remote_address} | Total: {len(self.clients)}")
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
    
    async def sensor_reader_task(self):
        """Continuously read sensors"""
        while True:
            temp, humidity, confidence = await self.dht.read()
            moisture = await self.soil.read()
            
            self.shared_data['temperature'] = temp
            self.shared_data['humidity'] = humidity
            self.shared_data['moisture'] = moisture
            self.shared_data['confidence'] = confidence
            
            await asyncio.sleep(1.0)
    
    async def broadcaster_task(self):
        """Broadcast sensor data to all clients"""
        while True:
            await asyncio.sleep(BROADCAST_INTERVAL)
            
            temp = self.shared_data.get('temperature')
            humidity = self.shared_data.get('humidity')
            moisture = self.shared_data.get('moisture')
            confidence = self.shared_data.get('confidence', 0.0)
            
            if temp is not None and humidity is not None and moisture is not None:
                market_warning = (temp > TEMP_THRESHOLD) or (moisture < MOISTURE_THRESHOLD)
                
                data = {
                    "type": "sensor_data",
                    "timestamp": datetime.now().isoformat(),
                    "node_id": "agrosphere_edge_001",
                    "sensor_data": {
                        "temperature_celsius": round(temp, 2),
                        "humidity_percent": round(humidity, 2),
                        "soil_moisture_percent": round(moisture, 2)
                    },
                    "confidence_score": round(confidence, 3),
                    "market_warning": market_warning,
                    "status": "CRITICAL" if market_warning else "NORMAL",
                    "alerts": []
                }
                
                if temp > TEMP_THRESHOLD:
                    data["alerts"].append(f"Heat stress: {temp:.1f}°C > {TEMP_THRESHOLD}°C")
                if moisture < MOISTURE_THRESHOLD:
                    data["alerts"].append(f"Drought stress: {moisture:.1f}% < {MOISTURE_THRESHOLD}%")
                
                message = json.dumps(data)
                await self.broadcast(message)
                
                # Console output
                print(f"📡 Broadcasting to {len(self.clients)} clients | Temp: {temp:.1f}°C | Moisture: {moisture:.1f}%")
    
    async def handle_client(self, websocket, path):
        """Handle individual WebSocket client connection"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                # Handle incoming messages from clients (optional)
                try:
                    data = json.loads(message)
                    if data.get("type") == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))
                except json.JSONDecodeError:
                    pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
    
    async def start(self):
        """Start WebSocket server and sensor tasks"""
        print("=" * 70)
        print("AgroSphere AI - Real-Time IoT WebSocket Server")
        print("=" * 70)
        print(f"WebSocket Server: ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
        print(f"DHT11: GPIO 27 | Soil Moisture: GPIO 17")
        print(f"Broadcast Interval: {BROADCAST_INTERVAL}s")
        print("=" * 70)
        print()
        
        # Start sensor reading task
        asyncio.create_task(self.sensor_reader_task())
        
        # Start broadcaster task
        asyncio.create_task(self.broadcaster_task())
        
        # Start WebSocket server
        async with websockets.serve(self.handle_client, WEBSOCKET_HOST, WEBSOCKET_PORT):
            print(f"🚀 Server running! Waiting for clients...")
            print(f"   Connect from: ws://YOUR_RPI_IP:{WEBSOCKET_PORT}")
            print()
            await asyncio.Future()  # Run forever
    
    def cleanup(self):
        """Cleanup resources"""
        self.dht.cleanup()
        self.soil.cleanup()


# ============================================================================
# MAIN
# ============================================================================

async def main():
    server = SensorWebSocketServer()
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
    finally:
        server.cleanup()
        print("✅ Cleanup complete")


if __name__ == "__main__":
    asyncio.run(main())
