"""
Pytest配置.

提供测试fixtures.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-16 - 设置TESTING环境变量，更新pytest-asyncio配置方式
"""

import os
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 设置测试环境标志（在导入app之前）
os.environ["TESTING"] = "true"

from app.config.settings import settings
from app.main import app

# 测试数据库URL
TEST_DATABASE_URL = settings.DATABASE_URL


# 使用pytest-asyncio的新配置方式
@pytest.fixture(scope="session")
def event_loop_policy():
    """配置事件循环策略."""
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(autouse=True)
def reset_app_dependency_overrides():
    """自动清理app的dependency_overrides，确保测试隔离."""
    # 测试前记录当前状态
    original_overrides = app.dependency_overrides.copy()
    yield
    # 测试后清理
    app.dependency_overrides.clear()
    # 恢复原始overrides（如果有）
    app.dependency_overrides.update(original_overrides)


@pytest.fixture
async def db_session():
    """创建数据库会话."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_factory() as session:
        yield session