#!/bin/bash
# FDAS迁移方案 - 回滚脚本（多容器 → 单容器）
# 用于迁移失败时恢复到原单容器方案

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="/tmp/fdas_migration"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "=========================================="
log_info "FDAS 回滚: 多容器 → 单容器"
log_info "=========================================="

# 确认回滚
confirm() {
    log_warn "回滚将停止多容器服务并恢复单容器！"
    read -p "确认回滚? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        log_info "取消回滚"
        exit 0
    fi
}

# 检查备份
check_backup() {
    log_info "[Step 1] 检查备份文件..."

    DB_BACKUP=$(ls "$BACKUP_DIR"/fdas_db_source_*.dump | head -1)
    if [ -z "$DB_BACKUP" ]; then
        log_error "未找到数据备份，无法回滚"
        exit 1
    fi

    log_info "使用备份: $DB_BACKUP"
}

# 停止多容器
stop_multi() {
    log_info "[Step 2] 停止多容器服务..."

    cd "$SCRIPT_DIR/../multi-container"
    docker-compose down

    log_info "多容器服务已停止"
}

# 启动单容器
start_single() {
    log_info "[Step 3] 启动单容器服务..."

    cd "$SCRIPT_DIR/../single-container"

    # 检查容器是否存在
    if docker ps -a --format '{{.Names}}' | grep -q "fdas-single"; then
        docker start fdas-single
    else
        # 需要重新部署
        log_warn "单容器不存在，需要重新部署"
        ./deploy.sh --action deploy
    fi

    # 等待PostgreSQL启动
    sleep 30
}

# 恢复数据库到单容器
restore_to_single() {
    log_info "[Step 4] 恢复数据库..."

    DB_BACKUP=$(ls "$BACKUP_DIR"/fdas_db_source_*.dump | head -1)

    # 如果是Docker容器
    if docker ps --format '{{.Names}}' | grep -q "fdas-single"; then
        # 断开连接
        docker exec fdas-single psql -U fdas -d postgres -c "
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'fdas' AND pid <> pg_backend_pid;
" 2>/dev/null || true

        # 重建数据库
        docker exec fdas-single psql -U fdas -d postgres -c "DROP DATABASE IF EXISTS fdas;"
        docker exec fdas-single psql -U fdas -d postgres -c "CREATE DATABASE fdas;"

        # 恢复数据
        docker exec -i fdas-single pg_restore -U fdas -d fdas \
            < "$DB_BACKUP"
    else
        # 本地PostgreSQL
        su - postgres -c "pg_restore -U fdas -d fdas --clean < $DB_BACKUP"
    fi

    log_info "数据库恢复完成"
}

# 重启单容器后端
restart_backend() {
    log_info "[Step 5] 重启后端服务..."

    if docker ps --format '{{.Names}}' | grep -q "fdas-single"; then
        docker exec fdas-single supervisorctl restart fdas_backend
    else
        supervisorctl restart fdas_backend
    fi

    sleep 10
}

# 验证回滚
verify_rollback() {
    log_info "[Step 6] 验证回滚..."

    if curl -f http://localhost:8000/api/health &> /dev/null; then
        log_info "健康检查通过"
    else
        log_error "健康检查失败"
        exit 1
    fi

    log_info "回滚验证通过"
}

# 主流程
main() {
    confirm
    check_backup
    stop_multi
    start_single
    restore_to_single
    restart_backend
    verify_rollback

    log_info "=========================================="
    log_info "回滚完成！"
    log_info "已恢复到单容器方案"
    log_info "=========================================="
}

main