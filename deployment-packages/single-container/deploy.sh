#!/bin/bash
# FDAS单容器部署方案 - 一站式部署脚本
# 使用方法: ./deploy.sh [--env-file .env] [--action deploy|stop|restart|logs|status]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 默认参数
ENV_FILE="${ENV_FILE:-.env}"
ACTION="${ACTION:-deploy}"

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
        --env-file) ENV_FILE="$2"; shift 2 ;;
        --action) ACTION="$2"; shift 2 ;;
        --help)
            echo "用法: ./deploy.sh [--env-file .env] [--action deploy|stop|restart|logs|status]"
            echo ""
            echo "Actions:"
            echo "  deploy  - 构建并启动服务"
            echo "  stop    - 停止服务"
            echo "  restart - 重启服务"
            echo "  logs    - 查看日志"
            echo "  status  - 查看状态"
            exit 0
            ;;
        *) log_error "未知参数: $1"; exit 1 ;;
    esac
done

# 检查环境变量文件
check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        log_warn "环境变量文件不存在，从模板创建..."
        cp config/.env.template "$ENV_FILE"
        log_warn "请编辑 $ENV_FILE 配置生产环境参数"
    fi

    # 加载环境变量
    source "$ENV_FILE"

    # 验证必要环境变量
    if [ -z "$SESSION_SECRET" ] || [ "$SESSION_SECRET" == "change-this-in-production-min-32-characters" ]; then
        log_error "SESSION_SECRET 未配置或使用了默认值"
        log_info "请编辑 $ENV_FILE 设置有效的SESSION_SECRET（至少32字符）"
        exit 1
    fi

    if [ ${#SESSION_SECRET} -lt 32 ]; then
        log_error "SESSION_SECRET 长度不足32字符"
        exit 1
    fi

    log_info "环境变量验证通过"
}

# 部署操作
deploy() {
    log_info "=========================================="
    log_info "FDAS单容器部署方案"
    log_info "=========================================="

    # Step 1: 检查Docker
    log_step "[Step 1] 检查Docker环境..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装"
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose未安装"
        exit 1
    fi
    log_info "Docker环境正常"

    # Step 2: 检查环境变量
    log_step "[Step 2] 检查环境变量..."
    check_env

    # Step 3: 构建镜像
    log_step "[Step 3] 构建应用镜像..."
    docker-compose build --no-cache

    # Step 4: 启动服务
    log_step "[Step 4] 启动服务..."
    docker-compose up -d

    # Step 5: 等待服务就绪
    log_step "[Step 5] 等待服务就绪..."
    log_info "等待数据库初始化（约60秒）..."
    sleep 60

    # Step 6: 健康检查
    log_step "[Step 6] 健康检查..."
    for i in {1..10}; do
        if curl -f http://localhost:8000/api/health &> /dev/null; then
            log_info "健康检查通过"
            break
        fi
        if [ $i -eq 10 ]; then
            log_error "健康检查失败"
            docker-compose logs
            exit 1
        fi
        log_info "等待服务启动... ($i/10)"
        sleep 10
    done

    # Step 7: 显示状态
    log_step "[Step 7] 显示服务状态..."
    docker-compose ps

    log_info "=========================================="
    log_info "部署完成！"
    log_info ""
    log_info "访问地址:"
    log_info "  前端页面: http://localhost:8000"
    log_info "  API文档:  http://localhost:8000/api/docs"
    log_info "  健康检查: http://localhost:8000/api/health"
    log_info ""
    log_info "默认账号: admin / admin123"
    log_warn "⚠️ 生产环境请立即修改默认密码"
    log_info "=========================================="
}

# 停止操作
stop() {
    log_info "停止FDAS单容器服务..."
    docker-compose down
    log_info "服务已停止"
}

# 重启操作
restart() {
    log_info "重启FDAS单容器服务..."
    docker-compose restart
    sleep 30
    curl -f http://localhost:8000/api/health || {
        log_error "重启后健康检查失败"
        exit 1
    }
    log_info "服务已重启"
}

# 查看日志
logs() {
    docker-compose logs -f
}

# 查看状态
status() {
    docker-compose ps
    echo ""
    echo "健康检查:"
    curl -s http://localhost:8000/api/health | python3 -m json.tool || echo "服务未响应"
}

# 主流程
case "$ACTION" in
    deploy) deploy ;;
    stop) stop ;;
    restart) restart ;;
    logs) logs ;;
    status) status ;;
    *)
        log_error "未知操作: $ACTION"
        echo "可用操作: deploy, stop, restart, logs, status"
        exit 1
        ;;
esac