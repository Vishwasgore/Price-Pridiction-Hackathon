@echo off
echo ======================================================================
echo AgroSphere AI - Backup Raspberry Pi Files
echo ======================================================================
echo.

cd /d "%~dp0\.."

echo Creating backup folder...
if not exist "RPI_BACKUP" mkdir RPI_BACKUP

echo.
echo Connecting to Raspberry Pi (192.168.1.18)...
echo You will be prompted for the password.
echo.

scp -r pi@192.168.1.18:/home/pi/agrosphere-iot/* RPI_BACKUP\

echo.
echo ======================================================================
if %ERRORLEVEL% EQU 0 (
    echo ✅ Backup completed successfully!
    echo Files saved to: %~dp0..\RPI_BACKUP\
) else (
    echo ❌ Backup failed. Check your connection and try again.
)
echo ======================================================================
echo.

pause
