@echo off
echo ======================================================================
echo AgroSphere AI - Starting Flask Backend Server
echo ======================================================================
echo.

cd /d "%~dp0\.."

echo Installing dependencies...
python -m pip install flask flask-cors

echo.
echo Starting Flask server on port 5000...
echo Dashboard will be available at: http://localhost:5000
echo.
echo Keep this window open!
echo Press Ctrl+C to stop the server
echo.

python backend\iot_receiver.py

pause
