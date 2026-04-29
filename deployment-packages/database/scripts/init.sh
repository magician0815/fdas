#!/bin/bash
# FDAS Database - 初始化脚本
# 使用方法: ./init.sh [--container fdas-db] [--drop-existing]

set -e

CONTAINER="${1:-fdas-db}"
DROP_EXISTING="${2:-false}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log_info "=========================================="
log_info "FDAS Database 初始化"
log_info "=========================================="

# 检查容器状态
check_container() {
    if docker ps --format '{{.Names}}' | grep -q "$CONTAINER"; then
        log_info "容器 $CONTAINER 正在运行"
    else
        log_error "容器 $CONTAINER 未运行"
        log_info "启动容器: docker start $CONTAINER"
        exit 1
    fi
}

# 初始化数据库
init_database() {
    log_info "执行数据库初始化..."

    if [ "$DROP_EXISTING" == "--drop-existing" ]; then
        log_info "删除现有数据..."
        docker exec -i $CONTAINER psql -U fdas -d postgres -c "DROP DATABASE IF EXISTS fdas;"
        docker exec -i $CONTAINER psql -U fdas -d postgres -c "CREATE DATABASE fdas;"
    fi

    # 执行初始化SQL
    docker exec -i $CONTAINER psql -U fdas -d fdas < "$SCRIPT_DIR/../init-db.sql"

    log_info "数据库初始化完成"
}

# 验证初始化结果
verify_init() {
    log_info "验证初始化结果..."

    # 检查表数量
    TABLE_COUNT=$(docker exec $CONTAINER psql -U fdas -d fdas -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

    if [ "$TABLE_COUNT" -lt 5 ]; then
        log_error "表数量异常: $TABLE_COUNT"
        exit 1
    fi

    log_info "表数量: $(echo $TABLE_COUNT | tr -d ' ')"

    # 检查初始数据
    USER_COUNT=$(docker exec $CONTAINER psql -U fdas -d fdas -t -c "SELECT COUNT(*) FROM users;")
    log_info "用户数量: $(echo $USER_COUNT | tr -d ' ')"

    MARKET_COUNT=$(docker exec $CONTAINER psql -U fdas -d fdas -t -c "SELECT COUNT(*) FROM markets;")
    log_info "市场数量: $(echo $MARKET_COUNT | tr -d ' ')"

    log_info "验证完成"
}

# 主流程
main() {
    check_container
    init_database
    verify_init

    log_info "=========================================="
    log_info "数据库初始化完成！"
    log_info "连接信息:"
    log_info "  Host: localhost"
    log_info "  Port: 5432"
    log_info "  Database: fdas"
    log_info "  User: fdas"
    log_info "=========================================="
}

main