#!/bin/bash
# FDAS运维脚本 - 查看状态
# 使用方法: ./status.sh [--方案 single|multi]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DEPLOY_MODE="${1:-multi}"

if [ "$DEPLOY_MODE" == "--方案" ] || [ "$DEPLOY_MODE" == "--mode" ]; then
    DEPLOY_MODE="$2"
fi

# 调用主脚本
$SCRIPT_DIR/fdas-ops.sh status --方案 $DEPLOY_MODE