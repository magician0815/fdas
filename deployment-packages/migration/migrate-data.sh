#!/bin/bash
# FDAS迁移方案 - 数据迁移脚本（单容器 → 多容器）
# 使用方法: ./migrate-data.sh [--source-container fdas-single]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SOURCE="${1:-fdas-single}"
BACKUP_DIR="/tmp/fdas_migration"
DATE=$(date +%Y%m%d_%H%M%S)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "=========================================="
log_info "FDAS 数据迁移: 单容器 → 多容器"
log_info "=========================================="

# Step 1: 准备迁移目录
prepare_dir() {
    log_info "[Step 1] 准备迁移目录..."
    mkdir -p "$BACKUP_DIR"
    rm -rf "$BACKUP_DIR/*"
}

# Step 2: 备份单容器数据
backup_source() {
    log_info "[Step 2] 备份单容器数据..."

    # 方式1: Docker容器内备份
    if docker ps --format '{{.Names}}' | grep -q "$SOURCE"; then
        log_info "从容器 $SOURCE 备份数据..."

        # 备份数据库
        docker exec $SOURCE pg_dump -U fdas -d fdas -F c \
            > "$BACKUP_DIR/fdas_db_source_$DATE.dump"

        # 备份数据卷
        docker exec $SOURCE tar czf /tmp/fdas_volumes.tar.gz \
            -C /var/log/fdas . \
            -C /opt/fdas/backend/logs . 2>/dev/null || true
        docker cp $SOURCE:/tmp/fdas_volumes.tar.gz "$BACKUP_DIR/fdas_volumes_source_$DATE.tar.gz"

        # 备份环境变量
        docker exec $SOURCE cat /opt/fdas/backend/app/.env > "$BACKUP_DIR/env_source_$DATE" 2>/dev/null || true

    # 方式2: 本地PostgreSQL备份（非Docker单容器）
    elif su - postgres -c "pg_isready -q" 2>/dev/null; then
        log_info "从本地PostgreSQL备份数据..."

        pg_dump -U fdas -d fdas -F c > "$BACKUP_DIR/fdas_db_source_$DATE.dump"

        tar czf "$BACKUP_DIR/fdas_volumes_source_$DATE.tar.gz" \
            -C /var/log/fdas . \
            -C /opt/fdas/backend/logs . 2>/dev/null || true

        cp /opt/fdas/backend/.env "$BACKUP_DIR/env_source_$DATE" 2>/dev/null || true

    else
        log_error "找不到数据源，请确认单容器运行状态"
        exit 1
    fi

    log_info "数据备份完成"
}

# Step 3: 验证备份完整性
verify_backup() {
    log_info "[Step 3] 验证备份完整性..."

    if [ ! -s "$BACKUP_DIR/fdas_db_source_$DATE.dump" ]; then
        log_error "数据库备份文件为空"
        exit 1
    fi

    BACKUP_SIZE=$(du -h "$BACKUP_DIR/fdas_db_source_$DATE.dump" | cut -f1)
    log_info "数据库备份大小: $BACKUP_SIZE"

    log_info "备份验证通过"
}

# Step 4: 停止单容器服务
stop_source() {
    log_info "[Step 4] 停止单容器服务..."

    if docker ps --format '{{.Names}}' | grep -q "$SOURCE"; then
        docker stop $SOURCE
        log_info "容器 $SOURCE 已停止"
    else
        log_info "本地服务停止需手动操作"
        log_warn "建议: supervisorctl stop all"
    fi
}

# Step 5: 生成迁移指令
generate_instructions() {
    log_info "[Step 5] 生成迁移指令..."

    cat > "$BACKUP_DIR/MIGRATE_INSTRUCTIONS.txt" << EOF
========================================
FDAS迁移指令
生成时间: $(date)
========================================

数据备份位置: $BACKUP_DIR

下一步操作:
1. 部署多容器方案
   cd deployment-packages/multi-container
   ./deploy.sh --env-file .env

2. 恢复数据库
   docker exec -i fdas-db pg_restore -U fdas -d fdas --no-owner --no-privileges \
       < $BACKUP_DIR/fdas_db_source_$DATE.dump

3. 恢复数据卷（如有）
   docker run --rm -v fdas-logs:/logs -v $BACKUP_DIR:/backup alpine \
       tar xzf /backup/fdas_volumes_source_$DATE.tar.gz -C /logs

4. 迁移环境变量
   cat $BACKUP_DIR/env_source_$DATE >> deployment-packages/multi-container/.env

5. 重启应用
   docker-compose restart fdas-app

6. 验证服务
   curl http://localhost:8000/api/health

========================================
完整迁移脚本: ./migrate-service.sh
========================================
EOF

    log_info "迁移指令已生成: $BACKUP_DIR/MIGRATE_INSTRUCTIONS.txt"
}

# 主流程
main() {
    prepare_dir
    backup_source
    verify_backup
    stop_source
    generate_instructions

    log_info "=========================================="
    log_info "数据迁移准备完成！"
    log_info ""
    log_info "备份位置: $BACKUP_DIR"
    log_info ""
    log_info "下一步:"
    log_info "  1. 查看迁移指令: cat $BACKUP_DIR/MIGRATE_INSTRUCTIONS.txt"
    log_info "  2. 执行服务迁移: ./migrate-service.sh"
    log_info "=========================================="
}

main