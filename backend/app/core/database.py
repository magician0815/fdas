"""
数据库连接池与ORM配置.

提供异步数据库引擎、会话工厂和Base模型类.

Author: FDAS Team
Created: 2026-04-03
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config.settings import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,        # 连接池大小
    max_overflow=20,     # 最大溢出连接
    pool_timeout=30,     # 获取连接超时（秒）
    pool_recycle=3600,   # 连接回收时间（秒）
    echo=settings.DEBUG, # SQL日志（调试模式）
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """
    SQLAlchemy模型基类.

    所有模型类继承此基类.
    """
    pass


async def get_db() -> AsyncSession:
    """
    获取数据库会话.

    用于FastAPI依赖注入.

    Yields:
        AsyncSession: 数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()