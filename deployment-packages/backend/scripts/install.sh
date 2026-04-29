#!/bin/bash
# FDAS Backend - 依赖安装脚本
# 使用方法: ./install.sh [--venv]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USE_VENV="${1:-true}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查Python版本
check_python_version() {
    PYTHON_VERSION=$(python3 -c "import sys; print(sys.version_info.major * 10 + sys.version_info.minor)")
    if [ "$PYTHON_VERSION" -lt 33 ]; then
        log_error "Python版本过低，需要3.13+，当前: $(python3 --version)"
        exit 1
    fi
    log_info "Python版本检查通过: $(python3 --version)"
}

# 安装TA-Lib C库（如果未安装）
install_talib_c() {
    if [ -f "/usr/lib/libta_lib.so" ]; then
        log_info "TA-Lib C库已安装"
        return 0
    fi

    log_info "安装TA-Lib C库..."

    # 检查编译工具
    if ! command -v gcc &> /dev/null; then
        log_warn "缺少编译工具，尝试安装..."
        apt-get update && apt-get install -y gcc g++ make wget || {
            log_error "无法安装编译工具，请手动安装: apt-get install gcc g++ make wget"
            exit 1
        }
    fi

    # 编译TA-Lib
    cd /tmp
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
    tar -xzf ta-lib-0.4.0-src.tar.gz
    cd ta-lib/
    ./configure --prefix=/usr
    make
    make install
    cd ..
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
    ldconfig

    log_info "TA-Lib C库安装完成"
}

# 安装Python依赖
install_python_deps() {
    log_info "安装Python依赖..."

    if [ "$USE_VENV" == "--venv" ] || [ "$USE_VENV" == "true" ]; then
        log_info "创建虚拟环境..."
        python3 -m venv venv
        source venv/bin/activate
    fi

    pip install --no-cache-dir -r requirements.txt

    # 验证TA-Lib Python包
    python -c "import talib; print('TA-Lib version:', talib.__version__)" || {
        log_error "TA-Lib Python包导入失败"
        exit 1
    }

    # 生成锁文件
    pip freeze > requirements.lock

    log_info "Python依赖安装完成"
}

# 主流程
main() {
    log_info "=========================================="
    log_info "FDAS Backend 依赖安装"
    log_info "=========================================="

    check_python_version
    install_talib_c
    install_python_deps

    log_info "=========================================="
    log_info "安装完成！"
    log_info "=========================================="

    if [ "$USE_VENV" == "--venv" ] || [ "$USE_VENV" == "true" ]; then
        log_info "虚拟环境已创建，激活命令:"
        log_info "  source venv/bin/activate"
    fi
}

main