#!/bin/bash
# FDAS单容器部署方案 - 用户创建与权限配置脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "=========================================="
log_info "FDAS单容器 - 用户创建与权限配置"
log_info "=========================================="

# 创建应用目录
create_directories() {
    log_info "创建应用目录..."

    mkdir -p /opt/fdas/backend
    mkdir -p /opt/fdas/frontend/dist
    mkdir -p /opt/fdas/config
    mkdir -p /opt/fdas/scripts
    mkdir -p /var/log/fdas
    mkdir -p /var/lib/postgresql/data
    mkdir -p /var/run/postgresql
    mkdir -p /var/run/supervisor

    log_info "目录创建完成"
}

# 创建用户
create_users() {
    log_info "创建系统用户..."

    # postgres用户（如果不存在）
    if ! id postgres &>/dev/null; then
        useradd --system --uid 999 --home-dir /var/lib/postgresql \
            --shell /usr/sbin/nologin postgres
    fi

    # fdas-backend用户
    if ! id fdas-backend &>/dev/null; then
        useradd --system --uid 1001 --home-dir /opt/fdas/backend \
            --shell /usr/sbin/nologin fdas-backend
    fi

    # fdas-frontend用户
    if ! id fdas-frontend &>/dev/null; then
        useradd --system --uid 1002 --home-dir /opt/fdas/frontend \
            --shell /usr/sbin/nologin fdas-frontend
    fi

    log_info "用户创建完成"
}

# 设置权限
set_permissions() {
    log_info "设置目录权限..."

    # 后端目录
    chown -R fdas-backend:fdas-backend /opt/fdas/backend

    # 前端目录
    chown -R fdas-frontend:fdas-frontend /opt/fdas/frontend/dist

    # 配置目录（root所有）
    chown -R root:root /opt/fdas/config
    chmod 700 /opt/fdas/config

    # 日志目录
    chown -R root:root /var/log/fdas
    chmod 755 /var/log/fdas

    # PostgreSQL目录
    chown -R postgres:postgres /var/lib/postgresql
    chown -R postgres:postgres /var/run/postgresql

    log_info "权限设置完成"
}

# 初始化PostgreSQL
init_postgresql() {
    log_info "初始化PostgreSQL..."

    if [ ! -d "/var/lib/postgresql/data/base" ]; then
        # 初始化数据库集群
        su - postgres -c "/usr/lib/postgresql/16/bin/initdb -D /var/lib/postgresql/data"

        # 启动PostgreSQL
        su - postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /var/lib/postgresql/data -l /var/log/fdas/postgresql.log start"
        sleep 5

        # 创建FDAS数据库用户和数据库
        su - postgres -c "psql -c \"CREATE USER fdas WITH PASSWORD 'fdas';\""
        su - postgres -c "psql -c \"CREATE DATABASE fdas OWNER fdas;\""
        su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE fdas TO fdas;\""

        # 停止PostgreSQL（等待supervisor启动）
        su - postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /var/lib/postgresql/data stop"

        log_info "PostgreSQL初始化完成"
    else
        log_info "PostgreSQL已初始化"
    fi
}

# 主流程
main() {
    create_directories
    create_users
    set_permissions
    init_postgresql

    log_info "=========================================="
    log_info "用户创建完成！"
    log_info ""
    log_info "用户信息:"
    log_info "  postgres    (UID 999) - PostgreSQL"
    log_info "  fdas-backend (UID 1001) - FastAPI后端"
    log_info "  fdas-frontend (UID 1002) - 前端静态文件"
    log_info ""
    log_info "下一步: ./install-python.sh 安装Python依赖"
    log_info "=========================================="
}

main