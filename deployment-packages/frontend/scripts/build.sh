#!/bin/bash
# FDAS Frontend - 构建脚本
# 使用方法: ./build.sh [--mode production|development]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../"

BUILD_MODE="${1:-production}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查Node.js版本
check_node_version() {
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        log_error "Node.js版本过低，需要18+，当前: $(node -v)"
        exit 1
    fi
    log_info "Node.js版本: $(node -v)"
}

# 安装依赖
install_deps() {
    log_info "安装前端依赖..."
    if [ -f "package-lock.json" ]; then
        npm ci --prefer-offline --no-audit
    else
        npm install
    fi
}

# 构建前端
build_frontend() {
    log_info "构建前端 ($BUILD_MODE模式)..."
    npm run build
}

# 验证构建产物
verify_build() {
    if [ ! -d "dist" ]; then
        log_error "构建失败，dist目录不存在"
        exit 1
    fi

    if [ ! -f "dist/index.html" ]; then
        log_error "构建失败，index.html不存在"
        exit 1
    fi

    log_info "构建产物验证通过"
    log_info "产物目录: $(ls -la dist/)"
}

# 主流程
main() {
    log_info "=========================================="
    log_info "FDAS Frontend 构建"
    log_info "=========================================="

    check_node_version
    install_deps
    build_frontend
    verify_build

    log_info "=========================================="
    log_info "构建完成！"
    log_info "产物目录: dist/"
    log_info "=========================================="
}

main