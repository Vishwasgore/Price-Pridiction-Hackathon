# ⚡ AgroSphere AI - Quick Start Guide

## 🎯 Run Everything in 3 Steps

### Step 1: Start Backend (Windows)
```powershell
Double-click: start_backend.bat
```
✅ Keep window open!

### Step 2: Start ngrok (Windows)
```powershell
Double-click: start_ngrok.bat
```
✅ Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Step 3: Run Sensors (Raspberry Pi)
```bash
cd ~/agrosphere-iot
nano sensor_to_backend.py
# Change line 22 to your ngrok URL
python3 sensor_to_backend.py
```
✅ Should see: `✅ Sent to backend | Success: 1`

---

## 🌐 View Dashboard

Open browser: `https://YOUR_NGROK_URL.ngrok.io`

---

## 🛑 Stop Everything

- **Raspberry Pi:** Press `Ctrl+C`
- **Windows Backend:** Press `Ctrl+C` in Terminal 1
- **ngrok:** Press `Ctrl+C` in Terminal 2

---

## 🔄 Restart Next Time

1. Start backend: `start_backend.bat`
2. Start ngrok: `start_ngrok.bat`
3. Copy new ngrok URL
4. Update Raspberry Pi script (line 22)
5. Run: `python3 sensor_to_backend.py`

---

## 📊 What You'll See

**Raspberry Pi Output:**
```json
{
  "temperature_celsius": 29.17,
  "humidity_percent": 36.33,
  "soil_moisture_percent": 0.0,
  "market_warning": true,
  "status": "CRITICAL"
}
✅ Sent to backend | Success: 1 | Errors: 0
```

**Dashboard:**
- Live temperature, humidity, soil moisture
- Real-time updates every 2 seconds
- Market warnings when thresholds exceeded

---

## 🐛 Quick Fixes

**"Python not found"** → Use `python` not `python3` on Windows

**"Connection failed"** → Check backend and ngrok are running

**"ngrok URL changed"** → Update Raspberry Pi script with new URL

**"No data"** → Check Raspberry Pi script is running

---

## 📁 Important Files

- `start_backend.bat` - Start Flask server
- `start_ngrok.bat` - Start ngrok tunnel
- `sensor_to_backend.py` - Raspberry Pi script
- `HOW_TO_RUN.md` - Detailed guide
- `API_INTEGRATION_GUIDE.md` - API docs

---

## 🎯 API Endpoints

```
GET  /                           # Dashboard
GET  /api/sensor-data            # Latest reading
GET  /api/sensor-history         # Last 100 readings
GET  /api/health                 # Health check
```

---

## 💡 Pro Tips

1. Keep backend and ngrok windows open
2. Save ngrok URL for Raspberry Pi
3. Test locally first: http://localhost:5000
4. Monitor backend terminal for logs
5. Free ngrok URL changes on restart

---

**Need more help? Check HOW_TO_RUN.md for detailed instructions!**
