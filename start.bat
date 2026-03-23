@echo off
echo Starting the application...

echo Starting backend...
start "Backend Server" cmd /k "cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8001"

timeout /t 3 /nobreak >nul

echo Starting frontend...
npm run electron:dev

pause
