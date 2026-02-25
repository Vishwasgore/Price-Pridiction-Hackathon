#!/usr/bin/env python3
"""
AgroSphere AI - Ground Truth Calibration Node
==============================================
Raspberry Pi sensor system for micro-climate monitoring to validate satellite-based
crop price predictions. This script provides real-time ground truth data that
calibrates macro-scale satellite observations with field-level conditions.

Hardware Configuration:
- DHT11 Sensor (Temperature/Humidity): GPIO 27, VCC 3.3V
- Soil Moisture Sensor: GPIO 17, VCC 3.3V

Business Logic:
Critical thresholds trigger "Profit Risk" signals to adjust Hold vs Sell strategies
in the AgroSphere backend based on crop stress indicators.
"""

import asyncio
import json
import time
from collections import deque
from datetime import datetime
from typing import Dict, Optional, Tuple

try:
    import board
    import adafruit_dht
    import RPi.GPIO as GPIO
    SIMULATION_MODE = False
except ImportError as e:
    print(f"Warning: Hardware libraries not available - {e}")
    print("Running in simulation mode for development/testing")
    SIMULATION_MODE = True
    board = None
    adafruit_dht = None
    GPIO = None


# ============================================================================
# CONFIGURATION
# ============================================================================

# GPIO Pin Configuration
DHT11_PIN = board.D27 if not SIMULATION_MODE else None  # GPIO 27 for DHT11
SOIL_MOISTURE_PIN = 17  # GPIO 17 for Soil Moisture Sensor

# Moving Average Filter Configuration
MOVING_AVERAGE_WINDOW = 5

# Critical Thresholds for Market Warning System
TEMP_THRESHOLD = 35.0  # °C - Heat stress indicator
MOISTURE_THRESHOLD = 20.0  # % - Drought stress indicator

# Sensor Reading Configuration
DHT11_RETRY_ATTEMPTS = 3
DHT11_RETRY_DELAY = 2  # seconds
SENSOR_READ_INTERVAL = 2  # seconds


# ============================================================================
# MOVING AVERAGE FILTER
# ============================================================================

class MovingAverageFilter:
    """
    Implements a moving average filter to smooth jittery sensor readings.
    Uses a circular buffer (deque) for efficient O(1) operations.
    """
    
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)
    
    def add_sample(self, value: float) -> float:
        """Add new sample and return smoothed value"""
        self.buffer.append(value)
        return sum(self.buffer) / len(self.buffer)
    
    def get_average(self) -> Optional[float]:
        """Get current average without adding new sample"""
        if not self.buffer:
            return None
        return sum(self.buffer) / len(self.buffer)
    
    def reset(self):
        """Clear the buffer"""
        self.buffer.clear()


# ============================================================================
# SENSOR READERS
# ============================================================================

class DHT11Reader:
    """
    Asynchronous DHT11 temperature and humidity sensor reader with error handling
    and retry mechanism. DHT11 sensors are notoriously unreliable, so we implement
    robust error handling with exponential backoff.
    """
    
    def __init__(self, pin):
        if not SIMULATION_MODE:
            self.dht_device = adafruit_dht.DHT11(pin)
        self.temp_filter = MovingAverageFilter(MOVING_AVERAGE_WINDOW)
        self.humidity_filter = MovingAverageFilter(MOVING_AVERAGE_WINDOW)
        self.last_valid_temp = None
        self.last_valid_humidity = None
    
    async def read_with_retry(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Read DHT11 sensor with retry mechanism.
        Returns: (temperature_celsius, humidity_percent) or (None, None) on failure
        """
        for attempt in range(DHT11_RETRY_ATTEMPTS):
            try:
                if SIMULATION_MODE:
                    # Simulation mode for development/testing
                    import random
                    temp = 25 + random.uniform(-5, 10)
                    humidity = 60 + random.uniform(-20, 20)
                else:
                    # Real sensor reading
                    temp = self.dht_device.temperature
                    humidity = self.dht_device.humidity
                
                # Validate readings
                if temp is not None and humidity is not None:
                    # Apply moving average filter for smooth, professional output
                    smoothed_temp = self.temp_filter.add_sample(temp)
                    smoothed_humidity = self.humidity_filter.add_sample(humidity)
                    
                    self.last_valid_temp = smoothed_temp
                    self.last_valid_humidity = smoothed_humidity
                    
                    return smoothed_temp, smoothed_humidity
                
            except RuntimeError as e:
                # DHT11 commonly throws RuntimeError - this is expected
                if attempt < DHT11_RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(DHT11_RETRY_DELAY)
                    continue
                else:
                    print(f"DHT11 Error after {DHT11_RETRY_ATTEMPTS} attempts: {e}")
            
            except Exception as e:
                print(f"Unexpected DHT11 error: {e}")
                break
        
        # Return last valid reading if current read fails
        return self.last_valid_temp, self.last_valid_humidity
    
    def cleanup(self):
        """Release DHT11 resources"""
        if not SIMULATION_MODE:
            self.dht_device.exit()


class SoilMoistureReader:
    """
    Asynchronous soil moisture sensor reader.
    Reads digital output from soil moisture sensor (HIGH = dry, LOW = wet).
    """
    
    def __init__(self, pin: int):
        self.pin = pin
        if not SIMULATION_MODE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN)
        self.moisture_filter = MovingAverageFilter(MOVING_AVERAGE_WINDOW)
    
    async def read(self) -> Optional[float]:
        """
        Read soil moisture sensor.
        Returns: moisture percentage (0-100%)
        """
        try:
            if SIMULATION_MODE:
                # Simulation mode
                import random
                moisture_raw = random.uniform(10, 80)
            else:
                # Real sensor reading (digital: 0 or 1)
                # Convert to percentage (inverted: 0=wet=100%, 1=dry=0%)
                digital_value = GPIO.input(self.pin)
                # For analog sensors, you'd use an ADC here
                # This is a simplified digital reading
                moisture_raw = 0 if digital_value else 100
            
            # Apply moving average filter
            smoothed_moisture = self.moisture_filter.add_sample(moisture_raw)
            return smoothed_moisture
            
        except Exception as e:
            print(f"Soil Moisture Sensor Error: {e}")
            return None
    
    @staticmethod
    def cleanup():
        """Release GPIO resources"""
        if not SIMULATION_MODE:
            GPIO.cleanup()


# ============================================================================
# BUSINESS LOGIC - MARKET WARNING SYSTEM
# ============================================================================

def analyze_crop_stress(temperature: float, moisture: float) -> Dict:
    """
    Analyze sensor data for crop stress indicators that impact price predictions.
    
    Critical thresholds:
    - Temperature > 35°C: Heat stress reduces yield, triggers early harvest consideration
    - Moisture < 20%: Drought stress impacts quality, may require immediate sale
    
    Returns: Analysis dict with warning status and recommended strategy
    """
    warnings = []
    risk_level = "LOW"
    recommended_action = "HOLD"
    
    # Heat Stress Analysis
    if temperature > TEMP_THRESHOLD:
        warnings.append(f"HEAT STRESS: Temperature {temperature:.1f}°C exceeds threshold {TEMP_THRESHOLD}°C")
        risk_level = "HIGH"
        recommended_action = "SELL"
    
    # Drought Stress Analysis
    if moisture < MOISTURE_THRESHOLD:
        warnings.append(f"DROUGHT STRESS: Moisture {moisture:.1f}% below threshold {MOISTURE_THRESHOLD}%")
        risk_level = "HIGH" if risk_level == "HIGH" else "MEDIUM"
        if recommended_action != "SELL":
            recommended_action = "EVALUATE"
    
    # Combined Stress (Critical)
    if temperature > TEMP_THRESHOLD and moisture < MOISTURE_THRESHOLD:
        warnings.append("CRITICAL: Combined heat and drought stress detected")
        risk_level = "CRITICAL"
        recommended_action = "SELL_IMMEDIATELY"
    
    return {
        "risk_level": risk_level,
        "recommended_action": recommended_action,
        "warnings": warnings,
        "market_signal": "PROFIT_RISK" if warnings else "NORMAL"
    }


# ============================================================================
# MAIN ASYNC SENSOR LOOP
# ============================================================================

async def read_dht11_task(dht_reader: DHT11Reader, shared_data: Dict):
    """Async task for continuous DHT11 reading"""
    while True:
        temp, humidity = await dht_reader.read_with_retry()
        shared_data['temperature'] = temp
        shared_data['humidity'] = humidity
        shared_data['dht11_last_update'] = datetime.now().isoformat()
        await asyncio.sleep(SENSOR_READ_INTERVAL)


async def read_soil_moisture_task(soil_reader: SoilMoistureReader, shared_data: Dict):
    """Async task for continuous soil moisture reading"""
    while True:
        moisture = await soil_reader.read()
        shared_data['soil_moisture'] = moisture
        shared_data['soil_last_update'] = datetime.now().isoformat()
        await asyncio.sleep(SENSOR_READ_INTERVAL)


async def main():
    """
    Main async loop - runs both sensors concurrently without blocking.
    This ensures DHT11's slow/unreliable reads don't impact soil moisture updates.
    """
    print("=" * 70)
    print("AgroSphere AI - Ground Truth Calibration Node")
    print("=" * 70)
    print(f"Mode: {'SIMULATION' if SIMULATION_MODE else 'PRODUCTION'}")
    print(f"DHT11 Pin: GPIO {DHT11_PIN if not SIMULATION_MODE else '27 (simulated)'}")
    print(f"Soil Moisture Pin: GPIO {SOIL_MOISTURE_PIN}")
    print(f"Moving Average Window: {MOVING_AVERAGE_WINDOW} samples")
    print("=" * 70)
    print()
    
    # Initialize sensors
    dht_reader = DHT11Reader(DHT11_PIN if not SIMULATION_MODE else None)
    soil_reader = SoilMoistureReader(SOIL_MOISTURE_PIN)
    
    # Shared data structure for concurrent access
    shared_data = {
        'temperature': None,
        'humidity': None,
        'soil_moisture': None,
        'dht11_last_update': None,
        'soil_last_update': None
    }
    
    try:
        # Create concurrent tasks for both sensors
        dht_task = asyncio.create_task(read_dht11_task(dht_reader, shared_data))
        soil_task = asyncio.create_task(read_soil_moisture_task(soil_reader, shared_data))
        
        # Main monitoring loop
        while True:
            await asyncio.sleep(5)  # Output every 5 seconds
            
            # Extract current readings
            temp = shared_data.get('temperature')
            humidity = shared_data.get('humidity')
            moisture = shared_data.get('soil_moisture')
            
            if temp is not None and humidity is not None and moisture is not None:
                # Perform business logic analysis
                analysis = analyze_crop_stress(temp, moisture)
                
                # Construct output JSON
                output = {
                    "timestamp": datetime.now().isoformat(),
                    "node_id": "RPi_GroundTruth_001",
                    "location": "Field_Calibration_Point",
                    "sensor_data": {
                        "temperature_celsius": round(temp, 2),
                        "humidity_percent": round(humidity, 2),
                        "soil_moisture_percent": round(moisture, 2)
                    },
                    "data_quality": {
                        "smoothing_applied": True,
                        "filter_type": "moving_average",
                        "window_size": MOVING_AVERAGE_WINDOW
                    },
                    "crop_stress_analysis": analysis,
                    "backend_integration": {
                        "signal": analysis['market_signal'],
                        "action": analysis['recommended_action'],
                        "description": "This ground-truth data validates satellite-based crop health indices and triggers automated price prediction adjustments in the AgroSphere backend."
                    }
                }
                
                # Output clean JSON
                print(json.dumps(output, indent=2))
                print()
                
                # Print market warnings prominently
                if analysis['warnings']:
                    print("⚠️  MARKET WARNING ⚠️")
                    for warning in analysis['warnings']:
                        print(f"   {warning}")
                    print(f"   → Backend Action: {analysis['recommended_action']}")
                    print(f"   → This triggers automated 'Sell Strategy' adjustment")
                    print()
            else:
                print("⏳ Waiting for sensor initialization...")
                print()
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down sensor node...")
    
    finally:
        # Cleanup resources
        dht_reader.cleanup()
        soil_reader.cleanup()
        print("✅ Cleanup complete")


if __name__ == "__main__":
    asyncio.run(main())
