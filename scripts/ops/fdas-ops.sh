#!/bin/bash
# FDAS日常运维脚本 - 主脚本
# 使用方法: ./fdas-ops.sh <command> [--方案 single|multi]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_title() { echo -e "${BLUE}[FDAS]${NC} $1"; }

# 默认方案
DEPLOY_MODE="${DEPLOY_MODE:-multi}"

# 参数解析
COMMAND="${1:-help}"
shift || true

while [[ $# -gt 0 ]]; do
    case $1 in
        --方案|--mode) DEPLOY_MODE="$2"; shift 2 ;;
        --help) COMMAND="help"; shift ;;
        *) shift ;;
    esac
done

# 获取部署目录
get_deploy_dir() {
    if [ "$DEPLOY_MODE" == "single" ]; then
        DEPLOY_DIR="$SCRIPT_DIR/../deployment-packages/single-container"
        COMPOSE_CMD="docker-compose -f $DEPLOY_DIR/docker-compose.yml"
        CONTAINER_NAME="fdas-single"
    else
        DEPLOY_DIR="$SCRIPT_DIR/../deployment-packages/multi-container"
        COMPOSE_CMD="docker-compose -f $DEPLOY_DIR/docker-compose.yml"
        CONTAINER_NAME="fdas-app"
    fi
}

# 显示帮助
show_help() {
    log_title "FDAS日常运维脚本"
    echo ""
    echo "用法: ./fdas-ops.sh <command> [--方案 single|multi]"
    echo ""
    echo "Commands:"
    echo "  start       启动所有服务"
    echo "  stop        停止所有服务"
    echo "  restart     重启所有服务"
    echo "  status      查看服务状态"
    echo "  logs        查看日志（支持 -f 跟随）"
    echo "  health      健康检查"
    echo "  backup      数据备份"
    echo "  restore     数据恢复"
    echo "  clean       清理临时文件"
    echo "  version     查看当前版本"
    echo "  help        显示帮助"
    echo ""
    echo "方案选项:"
    echo "  --方案 single  单容器部署方案"
    echo "  --方案 multi   多容器部署方案（默认）"
    echo ""
    echo "示例:"
    echo "  ./fdas-ops.sh start"
    echo "  ./fdas-ops.sh logs -f"
    echo "  ./fdas-ops.sh backup --full"
    echo "  ./fdas-ops.sh status --方案 single"
}

# 启动服务
start_service() {
    get_deploy_dir
    log_info "启动FDAS服务（$DEPLOY_MODE方案）..."
    cd $DEPLOY_DIR
    $COMPOSE_CMD up -d
    log_info "服务启动完成"
    sleep 10
    health_check
}

# 停止服务
stop_service() {
    get_deploy_dir
    log_info "停止FDAS服务（$DEPLOY_MODE方案）..."
    cd $DEPLOY_DIR
    $COMPOSE_CMD stop
    log_info "服务已停止"
}

# 重启服务
restart_service() {
    get_deploy_dir
    log_info "重启FDAS服务（$DEPLOY_MODE方案）..."
    cd $DEPLOY_DIR
    $COMPOSE_CMD restart
    sleep 30
    log_info "服务已重启"
    health_check
}

# 查看状态
show_status() {
    get_deploy_dir
    log_info "FDAS服务状态（$DEPLOY_MODE方案）:"
    cd $DEPLOY_DIR
    $COMPOSE_CMD ps
    echo ""
    health_check
}

# 查看日志
show_logs() {
    get_deploy_dir
    cd $DEPLOY_DIR
    if [ "$1" == "-f" ]; then
        $COMPOSE_CMD logs -f
    else
        $COMPOSE_CMD logs --tail=100
    fi
}

# 健康检查
health_check() {
    log_info "健康检查..."
    HEALTH_URL="http://localhost:8000/api/health"

    if curl -sf $HEALTH_URL > /dev/null 2>&1; then
        log_info "✓ 服务健康"
        curl -s $HEALTH_URL | python3 -m json.tool 2>/dev/null || curl -s $HEALTH_URL
    else
        log_error "✗ 服务异常"
        log_info "请检查日志: ./fdas-ops.sh logs"
    fi
}

# 数据备份
do_backup() {
    get_deploy_dir
    BACKUP_DIR="${BACKUP_DIR:-/var/backups/fdas}"
    DATE=$(date +%Y%m%d_%H%M%S)
    mkdir -p $BACKUP_DIR

    BACKUP_TYPE="${1:-full}"
    log_info "数据备份（$BACKUP_TYPE）..."

    case "$BACKUP_TYPE" in
        --full|full)
            if [ "$DEPLOY_MODE" == "multi" ]; then
                docker exec fdas-db pg_dump -U fdas -d fdas -F c > "$BACKUP_DIR/fdas_db_$DATE.dump"
            else
                docker exec $CONTAINER_NAME pg_dump -U fdas -d fdas -F c > "$BACKUP_DIR/fdas_db_$DATE.dump"
            fi
            ;;
        --data-only|data-only)
            if [ "$DEPLOY_MODE" == "multi" ]; then
                docker exec fdas-db pg_dump -U fdas -d fdas --data-only -F c > "$BACKUP_DIR/fdas_db_data_$DATE.dump"
            else
                docker exec $CONTAINER_NAME pg_dump -U fdas -d fdas --data-only -F c > "$BACKUP_DIR/fdas_db_data_$DATE.dump"
            fi
            ;;
    esac

    log_info "备份完成: $BACKUP_DIR"
    ls -lh $BACKUP_DIR | tail -5

    # 清理30天前的备份
    find $BACKUP_DIR -name "*.dump" -mtime +30 -delete 2>/dev/null || true
}

# 数据恢复
do_restore() {
    get_deploy_dir
    BACKUP_DIR="${BACKUP_DIR:-/var/backups/fdas}"

    log_warn "恢复将覆盖现有数据！"
    read -p "确认恢复? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        log_info "取消恢复"
        return
    fi

    BACKUP_FILE=$(ls -t $BACKUP_DIR/fdas_db_full_*.dump | head -1)
    if [ -z "$BACKUP_FILE" ]; then
        BACKUP_FILE=$(ls -t $BACKUP_DIR/fdas_db_*.dump | head -1)
    fi

    if [ -z "$BACKUP_FILE" ]; then
        log_error "未找到备份文件"
        return
    fi

    log_info "使用备份: $BACKUP_FILE"

    if [ "$DEPLOY_MODE" == "multi" ]; then
        docker exec fdas-db psql -U fdas -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'fdas';"
        docker exec fdas-db psql -U fdas -d postgres -c "DROP DATABASE IF EXISTS fdas;"
        docker exec fdas-db psql -U fdas -d postgres -c "CREATE DATABASE fdas;"
        docker exec -i fdas-db pg_restore -U fdas -d fdas < $BACKUP_FILE
    else
        docker exec $CONTAINER_NAME psql -U fdas -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'fdas';"
        docker exec $CONTAINER_NAME psql -U fdas -d postgres -c "DROP DATABASE IF EXISTS fdas;"
        docker exec $CONTAINER_NAME psql -U fdas -d postgres -c "CREATE DATABASE fdas;"
        docker exec -i $CONTAINER_NAME pg_restore -U fdas -d fdas < $BACKUP_FILE
    fi

    log_info "数据恢复完成"
    restart_service
}

# 清理临时文件
do_clean() {
    log_info "清理临时文件..."
    rm -rf /tmp/fdas_* 2>/dev/null || true
    docker system prune -f 2>/dev/null || true
    log_info "清理完成"
}

# 查看版本
show_version() {
    log_info "当前版本:"
    curl -s http://localhost:8000/api/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'版本: {d.get(\"version\",\"unknown\")}'); print(f'状态: {d.get(\"status\",\"unknown\")}')" 2>/dev/null || {
        log_error "服务未响应"
    }
}

# 主流程
case "$COMMAND" in
    start) start_service ;;
    stop) stop_service ;;
    restart) restart_service ;;
    status) show_status ;;
    logs) show_logs "$1" ;;
    health) health_check ;;
    backup) do_backup "$1" ;;
    restore) do_restore ;;
    clean) do_clean ;;
    version) show_version ;;
    help|--help|-h) show_help ;;
    *)
        log_error "未知命令: $COMMAND"
        show_help
        exit 1
        ;;
esac