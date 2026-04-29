"""
日志配置模块.

使用标准logging库实现统一日志格式和文件轮转.

Author: FDAS Team
Created: 2026-04-03
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config.settings import settings


def setup_logging() -> None:
    """
    配置日志系统.

    设置日志格式、级别、输出方式（控制台+文件轮转）.

    Args:
        None

    Returns:
        None
    """
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 获取根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    # 清除现有处理器
    root_logger.handlers.clear()

    # 创建格式器
    formatter = logging.Formatter(
        fmt=settings.LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台处理器（开发环境）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器（生产环境）
    log_file = log_dir / "app.log"
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=settings.LOG_FILE_MAX_SIZE,
        backupCount=settings.LOG_FILE_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器.

    Args:
        name: 日志器名称，通常使用模块名

    Returns:
        logging.Logger: 配置好的日志器实例
    """
    return logging.getLogger(name)