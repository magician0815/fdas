#!/bin/bash
# FDAS Backend - 停止脚本
# 使用方法: ./stop.sh [--force]

set -e

FORCE="${1:-false}"

echo "[INFO] 停止FDAS Backend..."

# 查找并停止uvicorn进程
if [ "$FORCE" == "--force" ]; then
    pkill -9 -f "uvicorn app.main:app" || echo "[INFO] 无运行进程"
else
    pkill -f "uvicorn app.main:app" || echo "[INFO] 无运行进程"
fi

# 等待进程结束
sleep 2

# 检查是否还有残留进程
REMAINING=$(pgrep -f "uvicorn app.main:app" || true)
if [ -n "$REMAINING" ]; then
    echo "[WARN] 仍有进程运行，PID: $REMAINING"
    if [ "$FORCE" != "--force" ]; then
        echo "[INFO] 使用 --force 强制停止"
    fi
else
    echo "[INFO] Backend已停止"
fi