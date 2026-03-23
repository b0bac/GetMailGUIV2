#!/bin/bash

# GetMail v2 启动脚本

echo "🚀 GetMail v2 启动中..."

# 启动后端
echo "启动后端 API..."
cd backend
python3 -m uvicorn main:app --host 127.0.0.1 --port 8001 &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 2

# 启动 Electron
echo "启动前端..."
npm run electron:dev

# 清理
kill $BACKEND_PID 2>/dev/null
