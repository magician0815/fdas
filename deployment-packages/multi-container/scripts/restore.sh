#!/bin/bash
# FDAS多容器部署方案 - 数据恢复脚本
# 使用方法: ./restore.sh [--backup-file backup.dump]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BACKUP_FILE="${1:-}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/fdas}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "=========================================="
log_info "FDAS多容器 - 数据恢复"
log_info "=========================================="

# 查找最新备份
if [ -z "$BACKUP_FILE" ]; then
    log_info "查找最新备份..."
    BACKUP_FILE=$(ls -t "$BACKUP_DIR"/fdas_db_full_*.dump | head -1)

    if [ -z "$BACKUP_FILE" ]; then
        log_error "未找到备份文件"
        exit 1
    fi

    log_info "使用备份: $BACKUP_FILE"
fi

# 确认恢复
log_warn "恢复将覆盖现有数据！"
read -p "确认恢复? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    log_info "取消恢复"
    exit 0
fi

# 检查服务状态
if ! docker ps --format '{{.Names}}' | grep -q "fdas-db"; then
    log_error "数据库容器未运行，请先启动服务"
    exit 1
fi

# 恢复数据库
log_info "恢复数据库..."

# 断开所有连接
docker exec fdas-db psql -U fdas -d postgres -c "
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'fdas' AND pid <> pg_backend_pid;
"

# 删除并重建数据库
docker exec fdas-db psql -U fdas -d postgres -c "DROP DATABASE IF EXISTS fdas;"
docker exec fdas-db psql -U fdas -d postgres -c "CREATE DATABASE fdas;"

# 恢复数据
docker exec -i fdas-db pg_restore -U fdas -d fdas --no-owner --no-privileges \
    < "$BACKUP_FILE"

# 恢复数据卷（如有备份）
VOLUME_BACKUP=$(ls -t "$BACKUP_DIR"/fdas_volumes_*.tar.gz | head -1)
if [ -n "$VOLUME_BACKUP" ]; then
    log_info "恢复数据卷..."
    docker run --rm \
        -v fdas-data:/data \
        -v fdas-logs:/logs \
        -v "$BACKUP_DIR:/backup" \
        alpine tar xzf "/backup/$(basename $VOLUME_BACKUP)" -C /
fi

# 重启应用服务
log_info "重启应用服务..."
docker-compose restart fdas-app

# 验证恢复
log_info "验证恢复结果..."
sleep 10

TABLE_COUNT=$(docker exec fdas-db psql -U fdas -d fdas -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' ')
log_info "表数量: $TABLE_COUNT"

if curl -f http://localhost:8000/api/health &> /dev/null; then
    log_info "健康检查通过"
else
    log_warn "健康检查未通过，请检查日志"
fi

log_info "=========================================="
log_info "恢复完成！"
log_info "=========================================="