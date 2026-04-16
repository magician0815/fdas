#!/bin/bash
# FDAS多容器部署方案 - 一站式部署脚本
# 使用方法: ./deploy.sh [--env-file .env] [--action deploy|stop|restart|logs|status|backup]

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
            echo "用法: ./deploy.sh [--env-file .env] [--action <action>]"
            echo ""
            echo "Actions:"
            echo "  deploy   - 构建并启动服务"
            echo "  stop     - 停止服务"
            echo "  restart  - 重启服务"
            echo "  logs     - 查看日志"
            echo "  status   - 查看状态"
            echo "  backup   - 备份数据"
            echo "  clean    - 清理容器和卷"
            exit 0
            ;;
        *) log_error "未知参数: $1"; exit 1 ;;
    esac
done

# 检查并创建环境变量文件
check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        log_warn "环境变量文件不存在，从模板创建..."
        cp config/.env.template "$ENV_FILE"

        # 自动生成安全的SESSION_SECRET
        log_info "自动生成安全的SESSION_SECRET..."
        GENERATED_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || \
                          openssl rand -base64 32 2>/dev/null || \
                          echo "fdas-$(date +%s)-$(head -c 16 /dev/urandom | od -An -tx1 | tr -d ' ')")

        # 替换.env中的SESSION_SECRET
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/^SESSION_SECRET=.*/SESSION_SECRET=${GENERATED_SECRET}/" "$ENV_FILE"
        else
            sed -i "s/^SESSION_SECRET=.*/SESSION_SECRET=${GENERATED_SECRET}/" "$ENV_FILE"
        fi

        log_warn "已自动生成SESSION_SECRET，请检查 $ENV_FILE 确认其他生产环境参数"
    fi

    # 加载环境变量
    source "$ENV_FILE"

    # 验证必要环境变量
    # 注意：docker-compose.yml已配置后备值，此处主要验证显式配置
    if [ -z "$SESSION_SECRET" ]; then
        log_error "SESSION_SECRET 未配置"
        log_info "请编辑 $ENV_FILE 设置SESSION_SECRET（至少32字符）"
        exit 1
    fi

    # 检查是否使用默认值（生产环境警告）
    if [[ "$SESSION_SECRET" == *"change-this"* ]] || [[ "$SESSION_SECRET" == *"dev-secret"* ]]; then
        log_warn "⚠️ 检测到使用默认SESSION_SECRET值，生产环境必须修改！"
        log_warn "建议运行: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
    fi

    if [ ${#SESSION_SECRET} -lt 32 ]; then
        log_error "SESSION_SECRET 长度不足32字符（当前: ${#SESSION_SECRET}字符）"
        exit 1
    fi

    log_info "环境变量验证通过"
}

# 部署操作
deploy() {
    log_info "=========================================="
    log_info "FDAS多容器部署方案"
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
    log_info "Docker版本: $(docker --version)"

    # Step 2: 检查环境变量
    log_step "[Step 2] 检查环境变量..."
    check_env

    # Step 3: 拉取基础镜像
    log_step "[Step 3] 拉取基础镜像..."
    docker pull postgres:16-alpine

    # Step 4: 构建应用镜像
    log_step "[Step 4] 构建应用镜像..."
    docker-compose build --no-cache

    # Step 5: 启动服务
    log_step "[Step 5] 启动服务..."
    docker-compose up -d

    # Step 6: 等待服务就绪（动态等待）
    log_step "[Step 6] 等待服务就绪..."
    log_info "等待数据库初始化..."

    # 动态等待数据库就绪（最多60秒）
    DB_READY=0
    for i in {1..12}; do
        if docker exec fdas-db pg_isready -U fdas -d fdas &> /dev/null; then
            log_info "数据库就绪"
            DB_READY=1
            break
        fi
        log_info "等待数据库启动... ($i/12)"
        sleep 5
    done

    if [ $DB_READY -eq 0 ]; then
        log_error "数据库启动超时"
        docker-compose logs fdas-db
        exit 1
    fi

    # 额外等待应用容器启动（数据库初始化脚本执行）
    log_info "等待应用容器启动（执行init-db.sql）..."
    sleep 10

    # Step 7: 健康检查（API + 前端）
    log_step "[Step 7] 健康检查..."

    # API健康检查
    API_READY=0
    for i in {1..15}; do
        if curl -f http://localhost:8000/api/health &> /dev/null; then
            log_info "API健康检查通过"
            API_READY=1
            break
        fi
        if [ $i -eq 15 ]; then
            log_error "API健康检查失败"
            docker-compose logs fdas-app
            exit 1
        fi
        log_info "等待API服务启动... ($i/15)"
        sleep 5
    done

    # 前端健康检查（检查index.html可访问）
    FRONTEND_READY=0
    for i in {1..5}; do
        FRONTEND_RESP=$(curl -s http://localhost:8000/ | grep -c "index.html" || true)
        if [ "$FRONTEND_RESP" -gt 0 ]; then
            log_info "前端服务检查通过"
            FRONTEND_READY=1
            break
        fi
        log_info "等待前端服务... ($i/5)"
        sleep 2
    done

    if [ $FRONTEND_READY -eq 0 ]; then
        log_warn "前端服务检查失败，但API已就绪，可能需要手动检查静态文件配置"
    fi

    # Step 8: 显示状态
    log_step "[Step 8] 显示服务状态..."
    docker-compose ps

    log_info "=========================================="
    log_info "部署完成！"
    log_info ""
    log_info "服务信息:"
    log_info "  fdas-db  : PostgreSQL数据库"
    log_info "  fdas-app : 应用服务（后端+前端）"
    log_info ""
    log_info "访问地址:"
    log_info "  前端页面: http://localhost:${APP_PORT:-8000}"
    log_info "  API文档:  http://localhost:${APP_PORT:-8000}/api/docs"
    log_info "  健康检查: http://localhost:${APP_PORT:-8000}/api/health"
    log_info ""
    log_info "关键依赖说明:"
    log_info "  - bcrypt>=4.0.0     : 密码哈希（admin用户密码必需）"
    log_info "  - psycopg2-binary   : APScheduler PostgreSQL同步驱动"
    log_info "  - slowapi           : API速率限制（login接口必需）"
    log_info ""
    log_info "默认账号: admin / admin123"
    log_warn "⚠️ 生产环境请立即修改默认密码"
    log_warn "⚠️ 生产环境请检查SESSION_SECRET是否为安全随机值"
    log_info "=========================================="
}

# 停止操作
stop() {
    log_info "停止FDAS多容器服务..."
    docker-compose down
    log_info "服务已停止"
}

# 重启操作
restart() {
    log_info "重启FDAS多容器服务..."
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
    docker-compose logs -f --tail=100
}

# 查看状态
status() {
    docker-compose ps
    echo ""
    echo "健康检查:"
    curl -s http://localhost:8000/api/health | python3 -m json.tool || echo "服务未响应"
    echo ""
    echo "数据库状态:"
    docker exec fdas-db pg_isready -U fdas
}

# 备份数据
backup() {
    log_info "备份数据..."
    BACKUP_DIR="${BACKUP_DIR:-/var/backups/fdas}"
    DATE=$(date +%Y%m%d_%H%M%S)

    mkdir -p "$BACKUP_DIR"

    # 备份数据库
    docker exec fdas-db pg_dump -U fdas -d fdas -F c > "$BACKUP_DIR/fdas_db_$DATE.dump"

    # 备份应用数据
    docker run --rm -v fdas-data:/data -v "$BACKUP_DIR:/backup" alpine \
        tar czf "/backup/fdas_data_$DATE.tar.gz" -C /data .

    log_info "备份完成: $BACKUP_DIR"
    ls -lh "$BACKUP_DIR" | tail -5
}

# 清理
clean() {
    log_warn "清理将删除所有容器和数据卷！"
    read -p "确认清理? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        log_info "取消清理"
        exit 0
    fi

    docker-compose down -v --rmi local
    log_info "清理完成"
}

# 主流程
case "$ACTION" in
    deploy) deploy ;;
    stop) stop ;;
    restart) restart ;;
    logs) logs ;;
    status) status ;;
    backup) backup ;;
    clean) clean ;;
    *)
        log_error "未知操作: $ACTION"
        echo "可用操作: deploy, stop, restart, logs, status, backup, clean"
        exit 1
        ;;
esac