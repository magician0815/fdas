#!/bin/bash
# FDAS单容器部署方案 - 数据库初始化脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "=========================================="
log_info "FDAS单容器 - 数据库初始化"
log_info "=========================================="

# 等待PostgreSQL就绪
wait_postgres() {
    log_info "等待PostgreSQL启动..."

    for i in {1..30}; do
        if su - postgres -c "pg_isready -q" 2>/dev/null; then
            log_info "PostgreSQL已就绪"
            return 0
        fi
        sleep 1
    done

    log_error "PostgreSQL未就绪"
    exit 1
}

# 执行初始化SQL
init_database() {
    log_info "执行数据库初始化SQL..."

    INIT_SQL="/opt/fdas/config/init-db.sql"

    if [ ! -f "$INIT_SQL" ]; then
        # 从docker目录复制
        cp "$SCRIPT_DIR/../docker/init-db.sql" "$INIT_SQL" || {
            log_error "init-db.sql文件不存在"
            exit 1
        }
    fi

    su - postgres -c "psql -d fdas -f $INIT_SQL" || {
        log_error "数据库初始化失败"
        exit 1
    }

    log_info "数据库初始化完成"
}

# 验证初始化
verify_init() {
    log_info "验证数据库初始化..."

    # 检查表数量
    TABLE_COUNT=$(su - postgres -c "psql -d fdas -t -c \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';\"" | tr -d ' ')

    if [ "$TABLE_COUNT" -lt 5 ]; then
        log_error "表数量异常: $TABLE_COUNT"
        exit 1
    fi

    log_info "表数量: $TABLE_COUNT"

    # 检查初始数据
    USER_COUNT=$(su - postgres -c "psql -d fdas -t -c \"SELECT COUNT(*) FROM users;\"" | tr -d ' ')
    log_info "用户数量: $USER_COUNT"

    MARKET_COUNT=$(su - postgres -c "psql -d fdas -t -c \"SELECT COUNT(*) FROM markets;\"" | tr -d ' ')
    log_info "市场数量: $MARKET_COUNT"

    SYMBOL_COUNT=$(su - postgres -c "psql -d fdas -t -c \"SELECT COUNT(*) FROM forex_symbols;\"" | tr -d ' ')
    log_info "外汇货币对数量: $SYMBOL_COUNT"
}

# 主流程
main() {
    wait_postgres
    init_database
    verify_init

    log_info "=========================================="
    log_info "数据库初始化完成！"
    log_info ""
    log_info "下一步: 启动Supervisor管理服务"
    log_info "  supervisord -c /opt/fdas/config/supervisord.conf"
    log_info "=========================================="
}

main