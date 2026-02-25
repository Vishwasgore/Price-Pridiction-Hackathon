# 🚀 AgroSphere AI - Complete Setup Guide

## 📋 What You Have

This project has 3 main parts:
1. **Raspberry Pi** - Reads sensors (DHT11 temperature/humidity + Soil moisture)
2. **Windows Backend** - Receives and stores sensor data
3. **ngrok** - Makes your backend accessible from internet

---

## 🎯 Quick Start (3 Steps)

### Step 1: Start Windows Backend

On your Windows PC:

**Option A: Double-click the file**
```
Double-click: start_backend.bat
```

**Option B: Manual command**
```powershell
cd "C:\Users\USER\Desktop\AgroSphere AI\IoT hardware"
python iot_receiver.py
```

✅ You should see:
```
🚀 AgroSphere AI - IoT Data Receiver
Server starting on http://0.0.0.0:5000
Dashboard: http://localhost:5000
```

**Keep this window open!**

---

### Step 2: Start ngrok (Make it Public)

Open a NEW PowerShell window:

**Option A: Double-click the file**
```
Double-click: start_ngrok.bat
```

**Option B: Manual command**
```powershell
cd "C:\Users\USER\Desktop\AgroSphere AI\IoT hardware"
.\ngrok.exe http 5000
```

✅ You should see something like:
```
Forwarding   https://abc123.ngrok.io -> http://localhost:5000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

**Keep this window open!**

---

### Step 3: Start Raspberry Pi Sensor

On your Raspberry Pi (via SSH):

```bash
# Navigate to folder
cd ~/agrosphere-iot

# Edit the script to add your ngrok URL
nano sensor_to_backend.py

# Find line 22 and change to your ngrok URL:
BACKEND_URL = "https://YOUR_NGROK_URL.ngrok.io/api/sensor-data"

# Save: Ctrl+X, then Y, then Enter

# Run the script
python3 sensor_to_backend.py
```

✅ You should see:
```
✅ Sent to backend | Success: 1 | Errors: 0
```

---

## 🌐 Access Your Dashboard

Open your browser and go to:
```
https://YOUR_NGROK_URL.ngrok.io
```

You'll see a live dashboard with real-time sensor data! 🎉

---

## 📊 Complete Step-by-Step Guide

### Part 1: Windows Setup (One-time)

#### 1.1 Install Python (if not installed)
- Download from: https://www.python.org/downloads/
- Install and check "Add Python to PATH"

#### 1.2 Install Dependencies
```powershell
cd "C:\Users\USER\Desktop\AgroSphere AI\IoT hardware"
python -m pip install flask flask-cors
```

#### 1.3 Download ngrok (if not done)
- Go to: https://ngrok.com/download
- Download Windows version
- Extract `ngrok.exe` to: `C:\Users\USER\Desktop\AgroSphere AI\IoT hardware\`

#### 1.4 Setup ngrok Account (One-time)
- Sign up at: https://dashboard.ngrok.com/signup
- Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
- Run this command (replace YOUR_TOKEN):
```powershell
cd "C:\Users\USER\Desktop\AgroSphere AI\IoT hardware"
.\ngrok.exe config add-authtoken YOUR_TOKEN
```

---

### Part 2: Raspberry Pi Setup (One-time)

#### 2.1 Connect to Raspberry Pi
```powershell
ssh pi@192.168.1.18
# Enter password when prompted
```

#### 2.2 Install Dependencies
```bash
# Install Python libraries
pip3 install --break-system-packages adafruit-circuitpython-dht adafruit-blinka RPi.GPIO requests

# Or if that doesn't work:
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip libgpiod2
pip3 install --break-system-packages adafruit-circuitpython-dht adafruit-blinka RPi.GPIO requests
```

#### 2.3 Create Project Folder
```bash
mkdir -p ~/agrosphere-iot
cd ~/agrosphere-iot
```

#### 2.4 Create Sensor Script
```bash
nano sensor_to_backend.py
```

Copy the entire script from: `IoT hardware/sensor_to_backend.py`

Save: Ctrl+X, then Y, then Enter

#### 2.5 Connect Hardware
- **DHT11 Sensor:**
  - VCC → Pin 1 (3.3V)
  - DATA → GPIO 27 (Pin 13)
  - GND → Pin 6 (Ground)

- **Soil Moisture Sensor:**
  - VCC → Pin 17 (3.3V)
  - DO → GPIO 17 (Pin 11)
  - GND → Pin 9 (Ground)

---

### Part 3: Running Everything

#### 3.1 Start Windows Backend
```powershell
# Terminal 1
cd "C:\Users\USER\Desktop\AgroSphere AI\IoT hardware"
python iot_receiver.py
```

Keep running!

#### 3.2 Start ngrok
```powershell
# Terminal 2 (NEW window)
cd "C:\Users\USER\Desktop\AgroSphere AI\IoT hardware"
.\ngrok.exe http 5000
```

Copy the HTTPS URL!

#### 3.3 Update Raspberry Pi Script
```bash
# On Raspberry Pi
cd ~/agrosphere-iot
nano sensor_to_backend.py

# Change line 22 to your ngrok URL:
BACKEND_URL = "https://YOUR_NGROK_URL.ngrok.io/api/sensor-data"

# Save and exit
```

#### 3.4 Run Raspberry Pi Script
```bash
python3 sensor_to_backend.py
```

---

## 🎯 What Should Happen

### On Windows (Terminal 1 - Backend):
```
🚀 AgroSphere AI - IoT Data Receiver
Server starting on http://0.0.0.0:5000
 * Running on http://192.168.1.8:5000
```

### On Windows (Terminal 2 - ngrok):
```
Forwarding   https://abc123.ngrok.io -> http://localhost:5000
```

### On Raspberry Pi:
```
AgroSphere AI - Real-Time Backend Integration
Backend URL: https://abc123.ngrok.io/api/sensor-data

{
  "timestamp": "2026-02-25T10:35:00.899954",
  "temperature_celsius": 29.17,
  "humidity_percent": 36.33,
  "soil_moisture_percent": 0.0,
  "market_warning": true,
  "status": "CRITICAL"
}
✅ Sent to backend | Success: 1 | Errors: 0
```

### In Your Browser:
Open: `https://abc123.ngrok.io`

You'll see a dashboard with live sensor data updating every 2 seconds!

---

## 🛑 How to Stop Everything

### Stop Raspberry Pi:
```bash
# Press Ctrl+C in the terminal
```

### Stop Windows Backend:
```powershell
# Press Ctrl+C in Terminal 1
```

### Stop ngrok:
```powershell
# Press Ctrl+C in Terminal 2
```

---

## 🔄 How to Restart

### Quick Restart (Same Day):

**Windows:**
1. Double-click `start_backend.bat`
2. Double-click `start_ngrok.bat`
3. Copy new ngrok URL

**Raspberry Pi:**
```bash
cd ~/agrosphere-iot
nano sensor_to_backend.py
# Update line 22 with new ngrok URL
python3 sensor_to_backend.py
```

### Why Update URL?
ngrok free tier gives you a new URL every time you restart. If you want a permanent URL, upgrade to ngrok paid plan.

---

## 📱 Share with Friends

Send them the ngrok URL:
```
https://YOUR_NGROK_URL.ngrok.io
```

They can:
- View live dashboard in browser
- Access API at: `https://YOUR_NGROK_URL.ngrok.io/api/sensor-data`
- Integrate into their services (see API_INTEGRATION_GUIDE.md)

---

## 🐛 Troubleshooting

### Problem: "Python not found"
**Solution:** Use `python` instead of `python3` on Windows

### Problem: "Module not found"
**Solution:** Install dependencies:
```powershell
python -m pip install flask flask-cors
```

### Problem: "ngrok.exe not found"
**Solution:** 
- Download from https://ngrok.com/download
- Extract to IoT hardware folder
- Make sure you're in the correct directory

### Problem: "Connection failed" on Raspberry Pi
**Solution:**
- Check Windows backend is running
- Check ngrok is running
- Verify ngrok URL is correct in sensor_to_backend.py
- Make sure you're using HTTPS (not HTTP)

### Problem: "DHT11 sensor not found"
**Solution:**
- Check wiring connections
- Verify GPIO 27 is correct
- Try running with sudo: `sudo python3 sensor_to_backend.py`

### Problem: Soil moisture always shows 0%
**Solution:**
- This is normal if sensor is not in soil/water
- Check GPIO 17 wiring
- Try touching sensor probes with wet fingers to test

### Problem: ngrok URL changes every time
**Solution:**
- This is normal for free tier
- Upgrade to paid plan for permanent URL
- Or deploy backend to cloud (AWS, Heroku, etc.)

---

## 📁 Project Structure

```
IoT hardware/
├── iot_receiver.py              # Flask backend (Windows)
├── sensor_to_backend.py         # Sensor script (Raspberry Pi)
├── start_backend.bat            # Quick start backend
├── start_ngrok.bat              # Quick start ngrok
├── ngrok.exe                    # ngrok executable
├── HOW_TO_RUN.md               # This file
├── API_INTEGRATION_GUIDE.md    # API documentation
├── QUICK_START.md              # Quick reference
└── integration_examples/
    └── python_client.py        # Example integration
```

---

## 🎓 Understanding the Flow

```
┌─────────────────┐
│  Raspberry Pi   │  Reads sensors every 2 seconds
│  (Sensors)      │  - DHT11: Temperature & Humidity
│                 │  - Soil: Moisture level
└────────┬────────┘
         │ HTTP POST (JSON)
         ▼
┌─────────────────┐
│  Windows PC     │  Receives and stores data
│  Flask Backend  │  - Stores last 100 readings
│  Port 5000      │  - Provides API endpoints
└────────┬────────┘
         │ Tunnel
         ▼
┌─────────────────┐
│     ngrok       │  Makes backend public
│  Public HTTPS   │  - Generates public URL
│                 │  - Handles SSL/HTTPS
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Your Friend    │  Access from anywhere
│  (Internet)     │  - View dashboard
│                 │  - Use API
│                 │  - Integrate services
└─────────────────┘
```

---

## 💡 Tips

1. **Keep terminals open** - Don't close the backend or ngrok windows
2. **Save ngrok URL** - You'll need it for Raspberry Pi
3. **Test locally first** - Use http://localhost:5000 before sharing
4. **Monitor logs** - Watch the backend terminal for incoming data
5. **Check connections** - Verify all 3 parts are running before troubleshooting

---

## 🚀 Next Steps

1. **Test the system** - Make sure all 3 parts are working
2. **Share the URL** - Give ngrok URL to your friend
3. **Integrate services** - Use API_INTEGRATION_GUIDE.md
4. **Monitor data** - Watch the dashboard for real-time updates
5. **Deploy to cloud** - For production, deploy to AWS/Heroku

---

## 📞 Need Help?

Check these files:
- **QUICK_START.md** - Quick reference guide
- **API_INTEGRATION_GUIDE.md** - How to use the API
- **NGROK_SETUP.md** - Detailed ngrok setup

---

**That's it! You're ready to run AgroSphere AI! 🌾**
