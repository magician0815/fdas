#!/bin/bash
# FDAS迁移方案 - 服务迁移脚本（单容器 → 多容器）
# 前置条件: 已执行migrate-data.sh备份数据

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="/tmp/fdas_migration"
DATE=$(date +%Y%m%d_%H%M%S)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

log_info "=========================================="
log_info "FDAS 服务迁移: 单容器 → 多容器"
log_info "=========================================="

# 检查备份文件
check_backup() {
    log_step "[Step 1] 检查备份文件..."

    DB_BACKUP=$(ls "$BACKUP_DIR"/fdas_db_source_*.dump | head -1)
    if [ -z "$DB_BACKUP" ]; then
        log_error "未找到数据库备份，请先执行 migrate-data.sh"
        exit 1
    fi

    log_info "数据库备份: $DB_BACKUP"
}

# 部署多容器方案
deploy_multi() {
    log_step "[Step 2] 部署多容器方案..."

    cd "$SCRIPT_DIR/../multi-container"

    # 创建环境变量（如果不存在）
    if [ ! -f ".env" ]; then
        cp config/.env.template .env

        # 合并原环境变量
        ENV_BACKUP=$(ls "$BACKUP_DIR"/env_source_* | head -1)
        if [ -n "$ENV_BACKUP" ]; then
            cat "$ENV_BACKUP" >> .env
            log_info "已合并原环境变量"
        fi

        log_warn "请检查 .env 配置是否正确"
        log_warn "特别注意: SESSION_SECRET, DB_PASSWORD"
    fi

    # 部署服务
    ./deploy.sh --action deploy || {
        log_error "部署失败"
        exit 1
    }

    cd "$SCRIPT_DIR"
}

# 恢复数据库
restore_database() {
    log_step "[Step 3] 恢复数据库..."

    DB_BACKUP=$(ls "$BACKUP_DIR"/fdas_db_source_*.dump | head -1)

    # 等待数据库就绪
    log_info "等待数据库就绪..."
    for i in {1..30}; do
        if docker exec fdas-db pg_isready -U fdas -q; then
            break
        fi
        sleep 1
    done

    # 断开连接
    docker exec fdas-db psql -U fdas -d postgres -c "
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'fdas' AND pid <> pg_backend_pid;
"

    # 删除并重建数据库
    docker exec fdas-db psql -U fdas -d postgres -c "DROP DATABASE IF EXISTS fdas;"
    docker exec fdas-db psql -U fdas -d postgres -c "CREATE DATABASE fdas;"

    # 恢复数据
    docker exec -i fdas-db pg_restore -U fdas -d fdas --no-owner --no-privileges \
        < "$DB_BACKUP"

    log_info "数据库恢复完成"
}

# 恢复数据卷
restore_volumes() {
    log_step "[Step 4] 恢复数据卷..."

    VOLUME_BACKUP=$(ls "$BACKUP_DIR"/fdas_volumes_source_*.tar.gz | head -1)

    if [ -n "$VOLUME_BACKUP" ]; then
        docker run --rm \
            -v fdas-logs:/logs \
            -v "$BACKUP_DIR:/backup" \
            alpine tar xzf "/backup/$(basename $VOLUME_BACKUP)" -C /logs

        log_info "数据卷恢复完成"
    else
        log_info "无数据卷备份"
    fi
}

# 重启应用
restart_app() {
    log_step "[Step 5] 重启应用..."

    cd "$SCRIPT_DIR/../multi-container"
    docker-compose restart fdas-app

    sleep 15
}

# 验证迁移
verify_migration() {
    log_step "[Step 6] 验证迁移..."

    # 健康检查
    if curl -f http://localhost:8000/api/health &> /dev/null; then
        log_info "健康检查通过"
    else
        log_error "健康检查失败"
        docker-compose logs fdas-app
        exit 1
    fi

    # 数据验证
    TABLE_COUNT=$(docker exec fdas-db psql -U fdas -d fdas -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' ')
    log_info "表数量: $TABLE_COUNT"

    USER_COUNT=$(docker exec fdas-db psql -U fdas -d fdas -t -c "SELECT COUNT(*) FROM users;" | tr -d ' ')
    log_info "用户数量: $USER_COUNT"

    log_info "迁移验证通过"
}

# 主流程
main() {
    check_backup
    deploy_multi
    restore_database
    restore_volumes
    restart_app
    verify_migration

    log_info "=========================================="
    log_info "服务迁移完成！"
    log_info ""
    log_info "原单容器服务已停止"
    log_info "多容器服务已启动"
    log_info ""
    log_info "访问地址: http://localhost:8000"
    log_info ""
    log_warn "建议观察24小时后，可清理原单容器数据"
    log_info "=========================================="
}

main