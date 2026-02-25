# 🌾 AgroSphere AI - IoT Hardware

Ground-truth calibration system for satellite-driven agricultural intelligence.

## 📁 Project Structure

```
IoT hardware/
├── 📄 README.md                    # This file
├── 📄 ngrok.exe                    # ngrok tunnel executable
│
├── 📂 docs/                        # 📚 All Documentation
│   ├── HOW_TO_RUN.md              # Complete setup guide
│   ├── QUICK_START.md             # Quick reference (3 steps)
│   ├── API_INTEGRATION_GUIDE.md   # API usage examples
│   ├── INSTALLATION.md            # Installation instructions
│   ├── NGROK_SETUP.md             # ngrok configuration
│   ├── REALTIME_SETUP.md          # Real-time streaming setup
│   ├── SIMPLE_GUIDE.md            # Simplified guide
│   └── BACKUP_RPI_FILES.md        # Backup instructions
│
├── 📂 scripts/                     # 🚀 Quick Start Scripts
│   ├── start_backend.bat          # Start Flask backend
│   ├── start_ngrok.bat            # Start ngrok tunnel
│   └── backup_rpi.bat             # Backup Raspberry Pi files
│
├── 📂 backend/                     # 💻 Windows Backend
│   ├── iot_receiver.py            # Flask server (receives data)
│   ├── requirements.txt           # Python dependencies
│   └── websocket_test_client.html # Test dashboard
│
├── 📂 raspberry_pi/                # 🍓 Raspberry Pi Code
│   ├── sensor_to_backend.py       # Main sensor script (HTTP)
│   ├── sensor_websocket_server.py # WebSocket server
│   ├── sensor_http_client.py      # HTTP client
│   ├── sensor_bridge.py           # Bridge script
│   ├── sensor_reader.py           # Basic reader
│   ├── requirements.txt           # RPi dependencies
│   └── requirements_realtime.txt  # Real-time dependencies
│
├── 📂 integration_examples/        # 💡 Integration Examples
│   └── python_client.py           # Python integration example
│
└── 📂 RPI_BACKUP/                  # 💾 Raspberry Pi Backups
    └── (backup files)
```

---

## ⚡ Quick Start

### 1. Start Backend (Windows)
```powershell
Double-click: scripts\start_backend.bat
```

### 2. Start ngrok (Windows)
```powershell
Double-click: scripts\start_ngrok.bat
```
Copy the HTTPS URL

### 3. Run Sensors (Raspberry Pi)
```bash
cd ~/agrosphere-iot
python3 sensor_to_backend.py
```

---

## 📚 Documentation

- **Getting Started:** `docs/HOW_TO_RUN.md`
- **Quick Reference:** `docs/QUICK_START.md`
- **API Integration:** `docs/API_INTEGRATION_GUIDE.md`

---

## 🎯 What This Does

1. **Raspberry Pi** reads sensors (DHT11 + Soil Moisture)
2. **Windows Backend** receives and stores data
3. **ngrok** makes it accessible from internet
4. **Dashboard** shows real-time data
5. **API** provides data for your services

---

## 🌐 Access Points

- **Dashboard:** `https://YOUR_NGROK_URL.ngrok.io`
- **API:** `https://YOUR_NGROK_URL.ngrok.io/api/sensor-data`
- **History:** `https://YOUR_NGROK_URL.ngrok.io/api/sensor-history`

---

## 🔧 Requirements

### Windows:
- Python 3.x
- Flask, flask-cors
- ngrok.exe

### Raspberry Pi:
- Python 3.x
- adafruit-circuitpython-dht
- adafruit-blinka
- RPi.GPIO
- requests

---

## 📊 Hardware Setup

**DHT11 (Temperature/Humidity):**
- VCC → Pin 1 (3.3V)
- DATA → GPIO 27
- GND → Pin 6 (Ground)

**Soil Moisture:**
- VCC → Pin 17 (3.3V)
- DO → GPIO 17
- GND → Pin 9 (Ground)

---

## 🆘 Need Help?

Check the documentation in the `docs/` folder:
- Having trouble? → `docs/HOW_TO_RUN.md`
- Quick setup? → `docs/QUICK_START.md`
- API integration? → `docs/API_INTEGRATION_GUIDE.md`

---

## 📦 Backup

To backup Raspberry Pi files:
```powershell
Double-click: scripts\backup_rpi.bat
```

Files will be saved to `RPI_BACKUP/` folder.

---

**AgroSphere AI** - Satellite-driven agricultural decision platform with ground-truth calibration.
