#!/bin/bash
# FDAS单容器部署方案 - Python依赖安装脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "=========================================="
log_info "FDAS单容器 - Python依赖安装"
log_info "=========================================="

# 检查Python版本
check_python() {
    PYTHON_VERSION=$(python3 -c "import sys; print(sys.version_info.major * 10 + sys.version_info.minor)")
    if [ "$PYTHON_VERSION" -lt 33 ]; then
        log_error "Python版本过低，需要3.13+"
        exit 1
    fi
    log_info "Python版本: $(python3 --version)"
}

# 创建虚拟环境
create_venv() {
    log_info "创建Python虚拟环境..."

    cd /opt/fdas/backend
    python3 -m venv venv
    source venv/bin/activate

    log_info "虚拟环境已创建"
}

# 安装依赖
install_deps() {
    log_info "安装Python依赖..."

    # 复制requirements.txt（如果存在）
    if [ -f "$SCRIPT_DIR/../backend/requirements.txt" ]; then
        cp "$SCRIPT_DIR/../backend/requirements.txt" requirements.txt
    fi

    pip install --no-cache-dir -r requirements.txt

    # 生成锁文件
    pip freeze > requirements.lock

    log_info "依赖安装完成"
}

# 验证TA-Lib
verify_talib() {
    log_info "验证TA-Lib..."

    python -c "import talib; print('TA-Lib version:', talib.__version__)" || {
        log_error "TA-Lib导入失败，请确保C库已安装"
        exit 1
    }

    log_info "TA-Lib验证通过"
}

# 设置权限
set_permissions() {
    log_info "设置虚拟环境权限..."

    chown -R fdas-backend:fdas-backend /opt/fdas/backend/venv

    log_info "权限设置完成"
}

# 主流程
main() {
    check_python
    create_venv
    install_deps
    verify_talib
    set_permissions

    log_info "=========================================="
    log_info "Python依赖安装完成！"
    log_info ""
    log_info "下一步: ./init-database.sh 初始化数据库"
    log_info "=========================================="
}

main