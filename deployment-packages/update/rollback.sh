#!/bin/bash
# FDAS增量更新方案 - 版本回滚脚本
# 使用方法: ./rollback.sh --version <版本号>

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_VERSION="${TARGET_VERSION:-}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 参数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        --version) TARGET_VERSION="$2"; shift 2 ;;
        --help)
            echo "用法: ./rollback.sh --version <版本号>"
            exit 0
            ;;
        *) log_error "未知参数: $1"; exit 1 ;;
    esac
done

if [ -z "$TARGET_VERSION" ]; then
    log_error "必须指定回滚版本 (--version)"
    exit 1
fi

log_info "=========================================="
log_info "FDAS 版本回滚"
log_info "目标版本: $TARGET_VERSION"
log_info "=========================================="

# 检查目标版本镜像
check_image() {
    log_info "[Step 1] 检查目标版本镜像..."

    if ! docker image inspect fdas-app:$TARGET_VERSION &> /dev/null; then
        log_error "目标版本镜像不存在: fdas-app:$TARGET_VERSION"
        log_info "可用镜像:"
        docker images fdas-app --format "{{.Repository}}:{{.Tag}}"
        exit 1
    fi

    log_info "镜像存在: fdas-app:$TARGET_VERSION"
}

# 查找备份
find_backup() {
    log_info "[Step 2] 查找备份..."

    BACKUP_DIR=$(ls -dt /var/backups/fdas/upgrade_*_to_$TARGET_VERSION* | head -1)

    if [ -z "$BACKUP_DIR" ]; then
        log_warn "未找到目标版本备份"
    else
        log_info "找到备份: $BACKUP_DIR"
    fi
}

# 恢复数据库
restore_database() {
    log_info "[Step 3] 恢复数据库..."

    if [ -n "$BACKUP_DIR" ] && [ -f "$BACKUP_DIR/db_backup.dump" ]; then
        log_info "从备份恢复数据库..."

        # 断开连接
        docker exec fdas-db psql -U fdas -d postgres -c "
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'fdas' AND pid <> pg_backend_pid;
"

        # 重建数据库
        docker exec fdas-db psql -U fdas -d postgres -c "DROP DATABASE IF EXISTS fdas;"
        docker exec fdas-db psql -U fdas -d postgres -c "CREATE DATABASE fdas;"

        # 恢复数据
        docker exec -i fdas-db pg_restore -U fdas -d fdas < "$BACKUP_DIR/db_backup.dump"

        log_info "数据库恢复完成"
    else
        log_info "无数据库备份，仅回滚镜像"
    fi
}

# 回滚镜像
rollback_image() {
    log_info "[Step 4] 回滚镜像..."

    cd "$SCRIPT_DIR/../multi-container"

    # 标记当前镜像
    CURRENT_VERSION=$(curl -s http://localhost:8000/api/health | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','unknown'))" 2>/dev/null || echo "latest")
    docker tag fdas-app:latest fdas-app:$CURRENT_VERSION 2>/dev/null || true

    # 回滚到目标版本
    docker tag fdas-app:$TARGET_VERSION fdas-app:rollback-temp

    # 重启容器
    docker-compose stop fdas-app
    docker-compose rm -f fdas-app
    docker tag fdas-app:rollback-temp fdas-app:latest
    docker-compose up -d fdas-app

    cd "$SCRIPT_DIR"

    log_info "镜像回滚完成"
}

# 验证回滚
verify_rollback() {
    log_info "[Step 5] 验证回滚..."

    sleep 30

    CURRENT_VERSION=$(curl -s http://localhost:8000/api/health | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','unknown'))" 2>/dev/null || echo "unknown")

    if [ "$CURRENT_VERSION" != "$TARGET_VERSION" ]; then
        log_warn "版本不匹配，当前: $CURRENT_VERSION，目标: $TARGET_VERSION"
    else
        log_info "版本回滚成功: $CURRENT_VERSION"
    fi

    if curl -f http://localhost:8000/api/health &> /dev/null; then
        log_info "健康检查通过"
    else
        log_error "健康检查失败"
        exit 1
    fi
}

# 主流程
main() {
    check_image
    find_backup
    restore_database
    rollback_image
    verify_rollback

    log_info "=========================================="
    log_info "回滚完成！"
    log_info "当前版本: $(curl -s http://localhost:8000/api/health | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','unknown'))" 2>/dev/null || echo "unknown")"
    log_info "=========================================="
}

main