#!/bin/bash
# FDAS单容器部署方案 - 系统依赖安装脚本
# 用于非Docker环境的手动部署

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "=========================================="
log_info "FDAS单容器 - 系统依赖安装"
log_info "=========================================="

# 检测系统类型
if [ -f /etc/debian_version ]; then
    DISTRO="debian"
    PKG_MANAGER="apt-get"
elif [ -f /etc/redhat-release ]; then
    DISTRO="redhat"
    PKG_MANAGER="yum"
else
    log_error "未知系统类型"
    exit 1
fi

log_info "系统类型: $DISTRO"

# 安装基础包
install_base_packages() {
    log_info "安装基础系统包..."

    if [ "$DISTRO" == "debian" ]; then
        apt-get update
        apt-get install -y --no-install-recommends \
            # 编译工具
            gcc g++ make wget curl \
            # PostgreSQL
            postgresql postgresql-contrib \
            # Nginx
            nginx \
            # Supervisor
            supervisor \
            # Node.js
            nodejs npm \
            # 工具
            procps net-tools iproute2 \
            # 清理
            && rm -rf /var/lib/apt/lists/*
    else
        yum install -y \
            gcc gcc-c++ make wget curl \
            postgresql postgresql-server \
            nginx \
            supervisor \
            nodejs npm \
            procps-ng net-tools iproute
    fi

    log_info "基础包安装完成"
}

# 安装TA-Lib C库
install_talib() {
    log_info "安装TA-Lib C库..."

    if [ -f /usr/lib/libta_lib.so ]; then
        log_info "TA-Lib已安装"
        return 0
    fi

    cd /tmp
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
    tar -xzf ta-lib-0.4.0-src.tar.gz
    cd ta-lib/
    ./configure --prefix=/usr
    make
    make install
    cd ..
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
    ldconfig

    log_info "TA-Lib安装完成"
}

# 验证安装
verify_install() {
    log_info "验证安装..."

    # 检查Python
    python3 --version || { log_error "Python未安装"; exit 1; }

    # 检查Node.js
    node --version || { log_error "Node.js未安装"; exit 1; }
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        log_error "Node.js版本过低，需要18+"
        exit 1
    fi

    # 检查TA-Lib
    [ -f /usr/lib/libta_lib.so ] || { log_error "TA-Lib未安装"; exit 1; }

    # 检查PostgreSQL
    which pg_ctl || { log_error "PostgreSQL未安装"; exit 1; }

    # 检查Supervisor
    which supervisord || { log_error "Supervisor未安装"; exit 1; }

    log_info "所有依赖验证通过"
}

# 主流程
main() {
    install_base_packages
    install_talib
    verify_install

    log_info "=========================================="
    log_info "系统依赖安装完成！"
    log_info ""
    log_info "下一步: ./setup-users.sh 创建用户"
    log_info "=========================================="
}

main