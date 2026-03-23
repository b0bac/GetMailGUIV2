@echo off
chcp 65001 >nul
echo 🚀 GetMail v2 启动中...

REM 启动后端
echo 启动后端 API...
cd backend
start /b python -m uvicorn main:app --host 127.0.0.1 --port 8001
cd ..

REM 等待后端启动
timeout /t 2 /nobreak >nul

REM 启动 Electron
echo 启动前端...
npm run electron:dev

pause
