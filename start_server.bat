@echo off
title YTMP4 - YouTube Converter Server
echo =====================================================
echo   YTMP4 - YouTube to MP3 / MP4 Converter
echo =====================================================
echo.
echo  Starting server... please wait.
echo.

REM Kill anything already on port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

REM Start the Flask server in background, then open browser
start "" /B python backend\server.py

REM Wait 2 seconds for the server to start
timeout /t 2 /nobreak >nul

echo  Opening browser at http://localhost:8000
start "" http://localhost:8000

echo.
echo  Server is running at http://localhost:8000
echo  Close this window to stop the server.
echo.

REM Keep the server alive
python backend\server.py
pause
