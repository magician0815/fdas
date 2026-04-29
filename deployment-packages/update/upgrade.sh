#!/bin/bash
# FDAS增量更新方案 - 版本升级脚本
# 使用方法: ./upgrade.sh --version <版本号> [--dry-run]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="${VERSION:-}"
DRY_RUN="${DRY_RUN:-false}"

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

# 参数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        --version) VERSION="$2"; shift 2 ;;
        --dry-run) DRY_RUN="true"; shift ;;
        --help)
            echo "用法: ./upgrade.sh --version <版本号> [--dry-run]"
            echo ""
            echo "参数:"
            echo "  --version  目标版本号（必填）"
            echo "  --dry-run  模拟运行，不实际执行"
            exit 0
            ;;
        *) log_error "未知参数: $1"; exit 1 ;;
    esac
done

if [ -z "$VERSION" ]; then
    log_error "必须指定目标版本 (--version)"
    exit 1
fi

log_info "=========================================="
log_info "FDAS 版本升级"
log_info "目标版本: $VERSION"
log_info "模拟模式: $DRY_RUN"
log_info "=========================================="

# 获取当前版本
get_current_version() {
    CURRENT_VERSION=$(curl -s http://localhost:8000/api/health 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','unknown'))" 2>/dev/null || echo "unknown")
    log_info "当前版本: $CURRENT_VERSION"
}

# 创建备份
create_backup() {
    log_step "[Step 1] 创建当前版本备份..."

    BACKUP_DIR="/var/backups/fdas/upgrade_${CURRENT_VERSION}_to_${VERSION}_$(date +%Y%m%d_%H%M%S)"

    if [ "$DRY_RUN" == "true" ]; then
        log_info "[模拟] 将备份到: $BACKUP_DIR"
    else
        mkdir -p "$BACKUP_DIR"

        # 备份数据库
        docker exec fdas-db pg_dump -U fdas -d fdas -F c > "$BACKUP_DIR/db_backup.dump"

        # 备份环境变量
        cd "$SCRIPT_DIR/../multi-container"
        cp .env "$BACKUP_DIR/env_backup"

        # 标记当前镜像
        docker tag fdas-app:latest fdas-app:$CURRENT_VERSION 2>/dev/null || true

        log_info "备份完成: $BACKUP_DIR"
    fi
}

# 检查版本变更日志
check_changelog() {
    log_step "[Step 2] 检查版本变更内容..."

    CHANGELOG_FILE="$SCRIPT_DIR/versions/$VERSION/CHANGELOG.md"
    if [ -f "$CHANGELOG_FILE" ]; then
        log_info "版本变更日志:"
        cat "$CHANGELOG_FILE"
    else
        log_warn "未找到版本变更日志: $CHANGELOG_FILE"
    fi
}

# 执行数据库迁移
run_db_migration() {
    log_step "[Step 3] 检查数据库迁移..."

    MIGRATION_FILE="$SCRIPT_DIR/versions/$VERSION/migrations.sql"
    if [ -f "$MIGRATION_FILE" ]; then
        log_info "需要执行数据库迁移"

        if [ "$DRY_RUN" == "true" ]; then
            log_info "[模拟] 将执行: $MIGRATION_FILE"
        else
            log_warn "执行数据库迁移..."
            docker exec -i fdas-db psql -U fdas -d fdas < "$MIGRATION_FILE"

            log_info "数据库迁移完成"
        fi
    else
        log_info "无需数据库迁移"
    fi
}

# 拉取新版本代码
pull_code() {
    log_step "[Step 4] 拉取新版本代码..."

    if [ "$DRY_RUN" == "true" ]; then
        log_info "[模拟] 将拉取代码"
    else
        cd "$SCRIPT_DIR/../.."

        # 检查是否有git仓库
        if [ -d ".git" ]; then
            git fetch origin
            git checkout "v$VERSION" || git checkout main
            git pull origin main
        else
            log_warn "非git仓库，请手动更新代码"
        fi

        cd "$SCRIPT_DIR"
    fi
}

# 构建新镜像
build_image() {
    log_step "[Step 5] 构建新版本镜像..."

    if [ "$DRY_RUN" == "true" ]; then
        log_info "[模拟] 将构建镜像"
    else
        cd "$SCRIPT_DIR/../multi-container"
        docker-compose build --no-cache --build-arg VERSION=$VERSION
        cd "$SCRIPT_DIR"
    fi
}

# 部署新版本
deploy_new() {
    log_step "[Step 6] 部署新版本..."

    if [ "$DRY_RUN" == "true" ]; then
        log_info "[模拟] 将重启应用"
    else
        cd "$SCRIPT_DIR/../multi-container"
        docker-compose up -d fdas-app

        # 等待健康检查
        log_info "等待服务启动..."
        sleep 30

        # 验证部署
        if ! curl -f http://localhost:8000/api/health &> /dev/null; then
            log_error "健康检查失败，执行回滚..."
            ./rollback.sh --version $CURRENT_VERSION
            exit 1
        fi

        cd "$SCRIPT_DIR"
    fi
}

# 验证更新
verify_upgrade() {
    log_step "[Step 7] 验证更新..."

    if [ "$DRY_RUN" == "false" ]; then
        NEW_VERSION=$(curl -s http://localhost:8000/api/health | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','unknown'))" 2>/dev/null || echo "unknown")

        if [ "$NEW_VERSION" != "$VERSION" ]; then
            log_warn "版本未更新到 $VERSION，当前: $NEW_VERSION"
        else
            log_info "版本更新成功: $CURRENT_VERSION -> $NEW_VERSION"
        fi
    fi
}

# 主流程
main() {
    get_current_version
    create_backup
    check_changelog
    run_db_migration
    pull_code
    build_image
    deploy_new
    verify_upgrade

    log_info "=========================================="
    if [ "$DRY_RUN" == "true" ]; then
        log_info "模拟完成，无实际更改"
    else
        log_info "升级完成！"
        log_info "备份位置: $BACKUP_DIR"
        log_info ""
        log_warn "如有问题，执行回滚:"
        log_warn "  ./rollback.sh --version $CURRENT_VERSION"
    fi
    log_info "=========================================="
}

main