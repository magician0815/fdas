#!/bin/bash
# FDAS Database - 备份脚本
# 使用方法: ./backup.sh [--full|--data-only] [--container fdas-db]

set -e

BACKUP_TYPE="${1:-full}"
CONTAINER="${2:-fdas-db}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/fdas}"
DATE=$(date +%Y%m%d_%H%M%S)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 创建备份目录
mkdir -p "$BACKUP_DIR"

log_info "=========================================="
log_info "FDAS Database 备份"
log_info "类型: $BACKUP_TYPE"
log_info "容器: $CONTAINER"
log_info "=========================================="

case "$BACKUP_TYPE" in
    --full|full)
        log_info "执行完整备份..."

        # 备份数据库（PostgreSQL自定义格式）
        docker exec $CONTAINER pg_dump -U fdas -d fdas -F c \
            > "$BACKUP_DIR/fdas_db_full_$DATE.dump"

        # 备份配置
        docker exec $CONTAINER cat /etc/postgresql/postgresql.conf \
            > "$BACKUP_DIR/postgresql_conf_$DATE.bak" || true

        ;;
    --data-only|data-only)
        log_info "执行数据备份..."

        docker exec $CONTAINER pg_dump -U fdas -d fdas --data-only -F c \
            > "$BACKUP_DIR/fdas_db_data_$DATE.dump"

        ;;
    --schema-only|schema-only)
        log_info "执行Schema备份..."

        docker exec $CONTAINER pg_dump -U fdas -d fdas --schema-only -F c \
            > "$BACKUP_DIR/fdas_db_schema_$DATE.dump"

        ;;
    *)
        log_error "未知备份类型: $BACKUP_TYPE"
        echo "可用类型: --full, --data-only, --schema-only"
        exit 1
        ;;
esac

# 清理30天前的旧备份
find "$BACKUP_DIR" -name "*.dump" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.bak" -mtime +30 -delete

log_info "=========================================="
log_info "备份完成！"
log_info "备份位置: $BACKUP_DIR"
ls -lh "$BACKUP_DIR" | tail -5
log_info "=========================================="