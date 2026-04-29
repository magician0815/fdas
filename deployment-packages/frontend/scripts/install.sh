#!/bin/bash
# FDAS Frontend - Node.js依赖安装脚本
# 使用方法: ./install.sh [--ci]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../"

USE_CI="${1:-false}"

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js未安装"
    echo "请安装Node.js 18+: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "[ERROR] Node.js版本过低，需要18+"
    exit 1
fi

echo "[INFO] Node.js版本: $(node -v)"
echo "[INFO] npm版本: $(npm -v)"

# 安装依赖
if [ "$USE_CI" == "--ci" ] && [ -f "package-lock.json" ]; then
    echo "[INFO] 使用npm ci安装（精确版本）..."
    npm ci --prefer-offline --no-audit
else
    echo "[INFO] 使用npm install安装..."
    npm install
fi

echo "[INFO] 依赖安装完成"
npm list --depth=0