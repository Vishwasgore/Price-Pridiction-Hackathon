# AgroSphere AI - Ground Truth Calibration Node
## Installation Guide for Raspberry Pi

This guide will help you set up the sensor system on your Raspberry Pi for the AgroSphere AI platform.

---

## Hardware Requirements

- **Raspberry Pi** (3B+, 4, or Zero W recommended)
- **DHT11 Temperature/Humidity Sensor**
- **Soil Moisture Sensor** (Digital or Analog)
- **Jumper Wires**
- **Breadboard** (optional)
- **Power Supply** (5V 2.5A minimum)

---

## Hardware Wiring

### DHT11 Sensor (Temperature/Humidity)
```
DHT11 Pin    →    Raspberry Pi Pin
-----------------------------------------
VCC          →    Pin 1 (3.3V)
DATA         →    GPIO 27 (Pin 13)
GND          →    Pin 6 (Ground)
```

### Soil Moisture Sensor
```
Sensor Pin   →    Raspberry Pi Pin
-----------------------------------------
VCC          →    Pin 17 (3.3V)
DO (Digital) →    GPIO 17 (Pin 11)
GND          →    Pin 9 (Ground)
```

**⚠️ Important:** Ensure all connections are secure and double-check polarity before powering on.

---

## Software Installation

### Step 1: Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 2: Install System Dependencies
```bash
# Install Python development headers
sudo apt-get install -y python3-dev python3-pip

# Install libgpiod (required for newer Raspberry Pi OS)
sudo apt-get install -y libgpiod2
```

### Step 3: Install Python Libraries
```bash
# Navigate to the IoT hardware directory
cd "IoT hardware"

# Install Python dependencies
pip3 install -r requirements.txt

# Alternative: Install individually
pip3 install adafruit-circuitpython-dht
pip3 install adafruit-blinka
pip3 install RPi.GPIO
```

### Step 4: Enable GPIO Access (if needed)
```bash
# Add your user to the gpio group
sudo usermod -a -G gpio $USER

# Reboot to apply changes
sudo reboot
```

---

## Running the Sensor Script

### Basic Execution
```bash
# Make script executable
chmod +x sensor_reader.py

# Run the script
python3 sensor_reader.py
```

### Run as Background Service (Production)
Create a systemd service for automatic startup:

```bash
# Create service file
sudo nano /etc/systemd/system/agrosphere-sensor.service
```

Add the following content:
```ini
[Unit]
Description=AgroSphere AI Ground Truth Sensor Node
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/IoT hardware
ExecStart=/usr/bin/python3 /home/pi/IoT hardware/sensor_reader.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable agrosphere-sensor.service
sudo systemctl start agrosphere-sensor.service

# Check status
sudo systemctl status agrosphere-sensor.service

# View logs
sudo journalctl -u agrosphere-sensor.service -f
```

---

## Testing & Verification

### Test in Simulation Mode
If you want to test the script without actual hardware:
```bash
# The script automatically detects missing hardware libraries
# and runs in simulation mode
python3 sensor_reader.py
```

### Verify Sensor Readings
1. Run the script and observe JSON output
2. Check that temperature, humidity, and moisture values are reasonable
3. Test threshold triggers by simulating extreme conditions

### Expected Output Format
```json
{
  "timestamp": "2026-02-24T10:30:45.123456",
  "node_id": "RPi_GroundTruth_001",
  "location": "Field_Calibration_Point",
  "sensor_data": {
    "temperature_celsius": 28.5,
    "humidity_percent": 65.3,
    "soil_moisture_percent": 45.2
  },
  "data_quality": {
    "smoothing_applied": true,
    "filter_type": "moving_average",
    "window_size": 5
  },
  "crop_stress_analysis": {
    "risk_level": "LOW",
    "recommended_action": "HOLD",
    "warnings": [],
    "market_signal": "NORMAL"
  },
  "backend_integration": {
    "signal": "NORMAL",
    "action": "HOLD",
    "description": "This ground-truth data validates satellite-based crop health indices..."
  }
}
```

---

## Troubleshooting

### DHT11 Sensor Issues
**Problem:** "RuntimeError: DHT sensor not found"
- Check wiring connections
- Ensure DHT11 is connected to GPIO 27
- Try adding a 10kΩ pull-up resistor between DATA and VCC

**Problem:** Frequent read errors
- This is normal for DHT11 sensors
- The script includes retry logic to handle this
- Consider upgrading to DHT22 for better reliability

### GPIO Permission Errors
**Problem:** "Permission denied" when accessing GPIO
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER
sudo reboot
```

### Library Installation Errors
**Problem:** "Failed building wheel for RPi.GPIO"
```bash
# Install build dependencies
sudo apt-get install -y python3-dev gcc
pip3 install --upgrade setuptools wheel
pip3 install RPi.GPIO
```

---

## Integration with AgroSphere Backend

### Sending Data to Backend API
Modify the script to POST JSON data to your backend:

```python
import aiohttp

async def send_to_backend(data):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://your-backend-api.com/api/ground-truth',
            json=data,
            headers={'Authorization': 'Bearer YOUR_API_KEY'}
        ) as response:
            return await response.json()
```

### MQTT Integration (Alternative)
For real-time streaming to your backend:
```bash
pip3 install paho-mqtt
```

---

## Performance Optimization

### Adjust Reading Intervals
Edit configuration in `sensor_reader.py`:
```python
SENSOR_READ_INTERVAL = 2  # Increase for less frequent reads
MOVING_AVERAGE_WINDOW = 5  # Adjust smoothing window
```

### Reduce CPU Usage
```bash
# Lower process priority
nice -n 10 python3 sensor_reader.py
```

---

## Security Considerations

1. **Change default credentials** on Raspberry Pi
2. **Use SSH keys** instead of passwords
3. **Enable firewall** if exposing to network
4. **Encrypt API communications** (HTTPS/TLS)
5. **Rotate API keys** regularly

---

## Support & Documentation

- **Hardware Datasheets:** See `/docs` folder
- **API Documentation:** Check backend repository
- **Issues:** Report to project maintainer

---

## License & Credits

Part of the AgroSphere AI platform - Satellite-driven agricultural decision system.
Ground truth calibration validates macro-scale satellite observations with field-level precision.
