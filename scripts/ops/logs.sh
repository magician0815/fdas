#!/bin/bash
# FDAS运维脚本 - 查看日志
# 使用方法: ./logs.sh [-f] [--方案 single|multi]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

FOLLOW="${1:-}"
DEPLOY_MODE="${2:-multi}"

if [ "$DEPLOY_MODE" == "--方案" ] || [ "$DEPLOY_MODE" == "--mode" ]; then
    DEPLOY_MODE="$3"
fi

# 调用主脚本
$SCRIPT_DIR/fdas-ops.sh logs $FOLLOW --方案 $DEPLOY_MODE