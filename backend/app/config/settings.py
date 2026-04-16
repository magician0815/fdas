"""
Pydantic Settings配置管理.

提供三层配置结构：基础配置、环境配置、业务配置.

Author: FDAS Team
Created: 2026-04-03
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """
    基础配置（与环境无关）.

    Attributes:
        LOG_FORMAT: 日志格式字符串
        LOG_LEVEL: 日志级别
        LOG_FILE_MAX_SIZE: 单个日志文件最大大小（字节）
        LOG_FILE_BACKUP_COUNT: 保留日志文件数量
        DEFAULT_MA_PERIOD: 默认MA计算周期
        DEFAULT_MACD_FAST: 默认MACD快线周期
        DEFAULT_MACD_SLOW: 默认MACD慢线周期
        DEFAULT_MACD_SIGNAL: 默认MACD信号线周期
    """

    LOG_FORMAT: str = "%(asctime)s %(levelname)s %(name)s %(message)s"
    LOG_LEVEL: str = "INFO"
    LOG_FILE_MAX_SIZE: int = 100 * 1024 * 1024  # 100MB
    LOG_FILE_BACKUP_COUNT: int = 30
    DEFAULT_MA_PERIOD: int = 20
    DEFAULT_MACD_FAST: int = 12
    DEFAULT_MACD_SLOW: int = 26
    DEFAULT_MACD_SIGNAL: int = 9


class EnvConfig(BaseSettings):
    """
    环境配置（与环境相关）.

    通过.env文件或环境变量加载.

    Attributes:
        DATABASE_URL: PostgreSQL数据库连接URL
        SESSION_SECRET: Session签名密钥
        DEBUG: 是否开启调试模式
        ALLOWED_ORIGINS: CORS允许的源列表
        APP_PORT: 应用端口
    """

    DATABASE_URL: str = "postgresql+asyncpg://fdas:fdas@localhost:5432/fdas"
    SESSION_SECRET: str = ""  # 强制从环境变量加载
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    APP_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


class BusinessConfig(BaseSettings):
    """
    业务配置（业务相关）.

    Attributes:
        DEFAULT_COLLECTION_TIME: 默认采集时间
        FX_DATA_LIMIT: 汇率数据查询限制条数
        CACHE_TTL_SECONDS: 缓存过期时间（秒）
    """

    DEFAULT_COLLECTION_TIME: str = "18:00"
    FX_DATA_LIMIT: int = 1000
    CACHE_TTL_SECONDS: int = 86400  # 24小时


class Settings(BaseConfig, EnvConfig, BusinessConfig):
    """
    综合配置类.

    继承三层配置，提供统一的配置访问接口.
    """

    pass


# 全局配置实例
settings = Settings()