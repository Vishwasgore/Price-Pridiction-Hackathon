# Expose Raspberry Pi Flask Server to Internet using ngrok

## What We're Doing:
Making your Flask server (running on Windows at http://192.168.1.8:5000) accessible from anywhere on the internet, so your friend can access the sensor data remotely.

## Step 1: Download ngrok

### Windows:
1. Go to: https://ngrok.com/download
2. Download the Windows version (ZIP file)
3. Extract to: `C:\Users\USER\Desktop\AgroSphere AI\IoT hardware\`
4. You should have: `ngrok.exe` in the IoT hardware folder

### Alternative - Direct Download:
```powershell
# Run in PowerShell (in IoT hardware folder)
Invoke-WebRequest -Uri "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip" -OutFile "ngrok.zip"
Expand-Archive -Path "ngrok.zip" -DestinationPath "."
Remove-Item "ngrok.zip"
```

## Step 2: Sign Up for ngrok (Free)

1. Go to: https://dashboard.ngrok.com/signup
2. Sign up (free account)
3. Copy your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken

## Step 3: Authenticate ngrok

```powershell
# In IoT hardware folder
.\ngrok.exe config add-authtoken YOUR_AUTH_TOKEN_HERE
```

## Step 4: Start Your Flask Server

```powershell
# In IoT hardware folder
python iot_receiver.py
```

Keep this running!

## Step 5: Start ngrok (New Terminal)

Open a NEW PowerShell window in the IoT hardware folder:

```powershell
.\ngrok.exe http 5000
```

You'll see output like:
```
Forwarding   https://abc123.ngrok.io -> http://localhost:5000
```

## Step 6: Update Raspberry Pi Script

Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)

On your Raspberry Pi, edit:
```bash
nano ~/agrosphere-iot/sensor_to_backend.py
```

Change line 22 to:
```python
BACKEND_URL = "https://abc123.ngrok.io/api/sensor-data"
```

Save and run:
```bash
python3 sensor_to_backend.py
```

## Step 7: Share with Your Friend

Your friend can now access:
- **Dashboard:** `https://abc123.ngrok.io`
- **Latest Data API:** `https://abc123.ngrok.io/api/sensor-data`
- **History API:** `https://abc123.ngrok.io/api/sensor-history`

## Important Notes:

1. **Free ngrok URL changes** every time you restart ngrok
2. **Keep both running:** Flask server AND ngrok
3. **For permanent URL:** Upgrade to ngrok paid plan or use a custom domain

## Troubleshooting:

**Problem:** ngrok shows "command not found"
- Make sure you're in the IoT hardware folder
- Use `.\ngrok.exe` (with .\ prefix on Windows)

**Problem:** Flask server not accessible
- Check Flask is running on port 5000
- Check Windows Firewall isn't blocking port 5000

**Problem:** Raspberry Pi can't connect
- Make sure you're using HTTPS (not HTTP) with ngrok URL
- Check the ngrok URL is correct (copy-paste carefully)

## Alternative: ngrok on Raspberry Pi

If you want to run ngrok directly on the Raspberry Pi instead:

```bash
# On Raspberry Pi
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz
tar xvzf ngrok-v3-stable-linux-arm64.tgz
sudo mv ngrok /usr/local/bin/

# Authenticate
ngrok config add-authtoken YOUR_AUTH_TOKEN

# Expose port 5000
ngrok http 5000
```

Then your Flask server would need to run on the Raspberry Pi instead of Windows.
