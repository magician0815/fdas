#!/bin/bash
# FDAS Database - 恢复脚本
# 使用方法: ./restore.sh [--backup-file backup.dump] [--container fdas-db]

set -e

BACKUP_FILE="${1:-}"
CONTAINER="${2:-fdas-db}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

BACKUP_DIR="${BACKUP_DIR:-/var/backups/fdas}"

log_info "=========================================="
log_info "FDAS Database 恢复"
log_info "=========================================="

# 如果未指定备份文件，使用最新的
if [ -z "$BACKUP_FILE" ]; then
    log_info "查找最新备份文件..."
    BACKUP_FILE=$(ls -t "$BACKUP_DIR"/fdas_db_full_*.dump | head -1)

    if [ -z "$BACKUP_FILE" ]; then
        log_error "未找到备份文件"
        exit 1
    fi

    log_info "使用最新备份: $BACKUP_FILE"
fi

# 确认恢复
log_warn "恢复将覆盖现有数据！"
read -p "确认恢复? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    log_info "取消恢复"
    exit 0
fi

# 检查容器
if ! docker ps --format '{{.Names}}' | grep -q "$CONTAINER"; then
    log_error "容器 $CONTAINER 未运行"
    exit 1
fi

# 恢复数据库
log_info "恢复数据库..."

# 先断开所有连接
docker exec $CONTAINER psql -U fdas -d postgres -c "
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'fdas' AND pid <> pg_backend_pid();
"

# 删除并重建数据库
docker exec $CONTAINER psql -U fdas -d postgres -c "DROP DATABASE IF EXISTS fdas;"
docker exec $CONTAINER psql -U fdas -d postgres -c "CREATE DATABASE fdas;"

# 恢复数据
docker exec -i $CONTAINER pg_restore -U fdas -d fdas --no-owner --no-privileges \
    < "$BACKUP_FILE"

# 验证恢复
log_info "验证恢复结果..."
TABLE_COUNT=$(docker exec $CONTAINER psql -U fdas -d fdas -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
log_info "表数量: $(echo $TABLE_COUNT | tr -d ' ')"

log_info "=========================================="
log_info "恢复完成！"
log_info "=========================================="