#!/bin/bash
# FDAS Backend - 启动脚本
# 使用方法: ./start.sh [--port 8000] [--workers 4] [--venv]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../"

# 默认参数
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-4}"
USE_VENV="${USE_VENV:-true}"

# 加载环境变量
if [ -f ".env" ]; then
    source .env
fi

# 激活虚拟环境
if [ "$USE_VENV" == "true" ] && [ -d "venv" ]; then
    source venv/bin/activate
fi

# 检查必要环境变量
if [ -z "$SESSION_SECRET" ]; then
    echo "[ERROR] SESSION_SECRET 未配置"
    exit 1
fi

# 检查数据库连接
if [ -n "$DATABASE_URL" ]; then
    echo "[INFO] 数据库连接: $DATABASE_URL"
fi

# 启动服务
echo "[INFO] 启动FDAS Backend..."
echo "[INFO] 端口: $PORT, Workers: $WORKERS"

uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers $WORKERS \
    --log-level info

# 或使用nohup后台运行：
# nohup uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers $WORKERS > logs/backend.log 2>&1 &