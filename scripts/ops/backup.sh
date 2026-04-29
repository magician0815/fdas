#!/bin/bash
# FDAS运维脚本 - 数据备份
# 使用方法: ./backup.sh [--full|--data-only] [--方案 single|multi]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BACKUP_TYPE="${1:-full}"
DEPLOY_MODE="${2:-multi}"

if [ "$BACKUP_TYPE" == "--方案" ] || [ "$BACKUP_TYPE" == "--mode" ]; then
    DEPLOY_MODE="$2"
    BACKUP_TYPE="full"
fi

# 调用主脚本
$SCRIPT_DIR/fdas-ops.sh backup $BACKUP_TYPE --方案 $DEPLOY_MODE