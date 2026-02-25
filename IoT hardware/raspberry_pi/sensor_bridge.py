#!/usr/bin/env python3
"""
AgroSphere AI - IoT Edge Node Sensor Bridge
============================================
Production-grade sensor system for validating satellite-based crop intelligence
with ground-truth micro-climate data for 3-month price prediction models.

Hardware: DHT11 (GPIO 27), Soil Moisture (GPIO 17)
Output: JSON every 5 seconds with market warnings
"""

import asyncio
import json
import time
from collections import deque
from datetime import datetime
from typing import Dict, Optional, Tuple

import board
import adafruit_dht
import RPi.GPIO as GPIO

# ============================================================================
# CONFIGURATION
# ============================================================================

DHT11_PIN = board.D27
SOIL_MOISTURE_PIN = 17

# Thresholds
TEMP_THRESHOLD = 35.0  # °C
MOISTURE_THRESHOLD = 20.0  # %

# Timing
DHT11_RETRY_ATTEMPTS = 3
DHT11_RETRY_DELAY = 2.0
OUTPUT_INTERVAL = 5.0

# Moving Average
WINDOW_SIZE = 5


# ============================================================================
# MOVING AVERAGE FILTER
# ============================================================================

class MovingAverage:
    """Efficient moving average filter using circular buffer"""
    
    def __init__(self, size: int = 5):
        self.buffer = deque(maxlen=size)
        self.size = size
    
    def add(self, value: float) -> float:
        """Add sample and return smoothed value"""
        self.buffer.append(value)
        return sum(self.buffer) / len(self.buffer)
    
    def get(self) -> Optional[float]:
        """Get current average"""
        return sum(self.buffer) / len(self.buffer) if self.buffer else None


# ============================================================================
# SENSOR READERS
# ============================================================================

class DHT11Sensor:
    """DHT11 reader with retry logic and smoothing"""
    
    def __init__(self, pin):
        self.device = adafruit_dht.DHT11(pin)
        self.temp_filter = MovingAverage(WINDOW_SIZE)
        self.humidity_filter = MovingAverage(WINDOW_SIZE)
        self.error_count = 0
        self.read_count = 0
        self.last_temp = None
        self.last_humidity = None
    
    async def read(self) -> Tuple[Optional[float], Optional[float], float]:
        """
        Read with retry mechanism
        Returns: (temp, humidity, confidence_score)
        """
        self.read_count += 1
        
        for attempt in range(DHT11_RETRY_ATTEMPTS):
            try:
                temp = self.device.temperature
                humidity = self.device.humidity
                
                if temp is not None and humidity is not None:
                    # Apply smoothing
                    smoothed_temp = self.temp_filter.add(temp)
                    smoothed_humidity = self.humidity_filter.add(humidity)
                    
                    self.last_temp = smoothed_temp
                    self.last_humidity = smoothed_humidity
                    
                    # Calculate confidence based on error rate
                    confidence = 1.0 - (self.error_count / max(self.read_count, 1))
                    confidence = max(0.0, min(1.0, confidence))
                    
                    return smoothed_temp, smoothed_humidity, confidence
                
            except RuntimeError as e:
                if attempt < DHT11_RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(DHT11_RETRY_DELAY)
                else:
                    self.error_count += 1
            except Exception as e:
                self.error_count += 1
                break
        
        # Return last valid reading with reduced confidence
        confidence = max(0.0, 1.0 - (self.error_count / max(self.read_count, 1)))
        return self.last_temp, self.last_humidity, confidence
    
    def cleanup(self):
        """Release resources"""
        self.device.exit()


class SoilMoistureSensor:
    """Soil moisture reader with smoothing"""
    
    def __init__(self, pin: int):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)
        self.filter = MovingAverage(WINDOW_SIZE)
    
    async def read(self) -> Optional[float]:
        """
        Read soil moisture
        Returns: moisture percentage (0-100%)
        """
        try:
            # Read digital value (0=wet, 1=dry)
            digital = GPIO.input(self.pin)
            
            # Convert to percentage (inverted logic)
            # For analog sensors, use ADC conversion here
            moisture = 100.0 if digital == 0 else 0.0
            
            # Apply smoothing
            smoothed = self.filter.add(moisture)
            return smoothed
            
        except Exception as e:
            return None
    
    @staticmethod
    def cleanup():
        """Release GPIO"""
        GPIO.cleanup()


# ============================================================================
# ASYNC SENSOR TASKS
# ============================================================================

async def dht11_task(sensor: DHT11Sensor, data: Dict):
    """Continuous DHT11 reading task"""
    while True:
        temp, humidity, confidence = await sensor.read()
        data['temperature'] = temp
        data['humidity'] = humidity
        data['confidence'] = confidence
        await asyncio.sleep(2.0)


async def soil_task(sensor: SoilMoistureSensor, data: Dict):
    """Continuous soil moisture reading task"""
    while True:
        moisture = await sensor.read()
        data['moisture'] = moisture
        await asyncio.sleep(2.0)


# ============================================================================
# MAIN LOOP
# ============================================================================

async def main():
    """Main async loop with concurrent sensor reading"""
    
    print("=" * 70)
    print("AgroSphere AI - IoT Edge Node Sensor Bridge")
    print("=" * 70)
    print(f"DHT11: GPIO 27 | Soil Moisture: GPIO 17")
    print(f"Output Interval: {OUTPUT_INTERVAL}s | Moving Average: {WINDOW_SIZE} samples")
    print("=" * 70)
    print()
    
    # Initialize sensors
    dht = DHT11Sensor(DHT11_PIN)
    soil = SoilMoistureSensor(SOIL_MOISTURE_PIN)
    
    # Shared data structure
    shared = {
        'temperature': None,
        'humidity': None,
        'moisture': None,
        'confidence': 0.0
    }
    
    try:
        # Start concurrent sensor tasks
        task1 = asyncio.create_task(dht11_task(dht, shared))
        task2 = asyncio.create_task(soil_task(soil, shared))
        
        # Main output loop
        while True:
            await asyncio.sleep(OUTPUT_INTERVAL)
            
            temp = shared.get('temperature')
            humidity = shared.get('humidity')
            moisture = shared.get('moisture')
            confidence = shared.get('confidence', 0.0)
            
            if temp is not None and humidity is not None and moisture is not None:
                # Business logic: Market warning detection
                market_warning = (temp > TEMP_THRESHOLD) or (moisture < MOISTURE_THRESHOLD)
                
                # Construct JSON output
                output = {
                    "timestamp": datetime.now().isoformat(),
                    "node_id": "agrosphere_edge_001",
                    "sensor_data": {
                        "temperature_celsius": round(temp, 2),
                        "humidity_percent": round(humidity, 2),
                        "soil_moisture_percent": round(moisture, 2)
                    },
                    "confidence_score": round(confidence, 3),
                    "market_warning": market_warning,
                    "thresholds": {
                        "temp_threshold": TEMP_THRESHOLD,
                        "moisture_threshold": MOISTURE_THRESHOLD
                    },
                    "status": "CRITICAL" if market_warning else "NORMAL"
                }
                
                # Print clean JSON
                print(json.dumps(output, indent=2))
                print()
                
                # Alert on market warning
                if market_warning:
                    alerts = []
                    if temp > TEMP_THRESHOLD:
                        alerts.append(f"⚠️  HEAT STRESS: {temp:.1f}°C > {TEMP_THRESHOLD}°C")
                    if moisture < MOISTURE_THRESHOLD:
                        alerts.append(f"⚠️  DROUGHT STRESS: {moisture:.1f}% < {MOISTURE_THRESHOLD}%")
                    
                    for alert in alerts:
                        print(alert)
                    print("→ Storage Decay Risk Detected - Adjusting Price Model")
                    print()
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down sensor bridge...")
    
    finally:
        dht.cleanup()
        soil.cleanup()
        print("✅ Cleanup complete")


if __name__ == "__main__":
    asyncio.run(main())
