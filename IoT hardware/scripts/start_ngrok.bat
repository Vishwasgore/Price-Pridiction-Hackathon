@echo off
echo ======================================================================
echo AgroSphere AI - Starting ngrok Tunnel
echo ======================================================================
echo.

cd /d "%~dp0\.."

if not exist "ngrok.exe" (
    echo ERROR: ngrok.exe not found!
    echo.
    echo Please download ngrok from: https://ngrok.com/download
    echo Extract ngrok.exe to: %~dp0\..\
    echo.
    pause
    exit /b 1
)

echo Starting ngrok tunnel to port 5000...
echo.
echo Copy the HTTPS URL that appears below and share it with your friend!
echo Example: https://abc123.ngrok.io
echo.

..\ngrok.exe http 5000

pause
