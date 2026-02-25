# 📦 Backup Raspberry Pi Files to Windows

## 🎯 Quick Backup Command

Run this on your Windows PowerShell:

```powershell
# Navigate to your project folder
cd "C:\Users\USER\Desktop\AgroSphere AI"

# Create backup folder
mkdir "IoT hardware\RPI_Backup"

# Copy all files from Raspberry Pi to Windows
scp -r pi@192.168.1.18:/home/pi/agrosphere-iot/* "IoT hardware\RPI_Backup\"
```

Enter your Raspberry Pi password when prompted.

---

## 📁 What Will Be Backed Up

All files from:
```
/home/pi/agrosphere-iot/IoT hardware/
```

Will be copied to:
```
C:\Users\USER\Desktop\AgroSphere AI\IoT hardware\RPI_Backup\
```

---

## 🔄 Alternative: Manual Backup

If SCP doesn't work, use WinSCP:

1. Download WinSCP: https://winscp.net/eng/download.php
2. Install and open WinSCP
3. Connect to Raspberry Pi:
   - Host: `192.168.1.18`
   - Username: `pi`
   - Password: (your password)
4. Navigate to: `/home/pi/agrosphere-iot/IoT hardware/`
5. Drag and drop all files to Windows folder

---

## ✅ Verify Backup

After copying, check:
```powershell
dir "IoT hardware\RPI_Backup"
```

You should see all your Raspberry Pi files!

---

## 🔄 Restore to Raspberry Pi

If you need to restore files back to Raspberry Pi:

```powershell
scp -r "IoT hardware\RPI_Backup\*" pi@192.168.1.18:/home/pi/agrosphere-iot/
```

---

## 📅 Regular Backups

Create a backup script `backup_rpi.bat`:

```batch
@echo off
echo Backing up Raspberry Pi files...
scp -r pi@192.168.1.18:/home/pi/agrosphere-iot/* "IoT hardware\RPI_Backup\"
echo Backup complete!
pause
```

Double-click to run anytime!
