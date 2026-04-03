"""
Session服务测试.

测试Session CRUD功能.

Author: FDAS Team
Created: 2026-04-03
"""

import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.session_service import SessionService
from app.services.user_service import UserService
from app.services.auth_service import hash_password


@pytest.fixture
def session_service():
    """Session服务实例."""
    return SessionService()


@pytest.fixture
def user_service():
    """用户服务实例."""
    return UserService()


@pytest.mark.asyncio
async def test_create_session(db_session: AsyncSession, user_service: UserService):
    """测试创建Session."""
    # 使用唯一用户名
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    user = await user_service.create_user(
        db=db_session,
        username=unique_username,
        password="test123456",
        role="user",
    )

    # 创建Session
    service = SessionService()
    session = await service.create_session(
        db=db_session,
        user_id=user.id,
        expires_hours=24,
    )

    assert session is not None
    assert session.user_id == user.id
    # 注意：session.expires_at是timezone-aware，需要用timezone-aware比较
    from datetime import timezone
    assert session.expires_at.replace(tzinfo=None) > datetime.utcnow()


@pytest.mark.asyncio
async def test_get_session_by_id(db_session: AsyncSession, user_service: UserService):
    """测试根据ID获取Session."""
    # 使用唯一用户名
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    user = await user_service.create_user(
        db=db_session,
        username=unique_username,
        password="test123456",
        role="user",
    )

    service = SessionService()
    created = await service.create_session(
        db=db_session,
        user_id=user.id,
        expires_hours=24,
    )

    # 获取Session
    session = await service.get_session_by_id(db_session, created.id)

    assert session is not None
    assert session.id == created.id


@pytest.mark.asyncio
async def test_delete_session(db_session: AsyncSession, user_service: UserService):
    """测试删除Session."""
    # 使用唯一用户名
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    user = await user_service.create_user(
        db=db_session,
        username=unique_username,
        password="test123456",
        role="user",
    )

    service = SessionService()
    created = await service.create_session(
        db=db_session,
        user_id=user.id,
        expires_hours=24,
    )

    # 删除Session
    success = await service.delete_session(db_session, created.id)
    assert success is True

    # 验证已删除
    session = await service.get_session_by_id(db_session, created.id)
    assert session is None


@pytest.mark.asyncio
async def test_cleanup_expired_sessions(db_session: AsyncSession, user_service: UserService):
    """测试清理过期Session."""
    # 使用唯一用户名
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    user = await user_service.create_user(
        db=db_session,
        username=unique_username,
        password="test123456",
        role="user",
    )

    service = SessionService()

    # 创建已过期Session
    await service.create_session(
        db=db_session,
        user_id=user.id,
        expires_hours=-1,  # 已过期
    )

    # 创建有效Session
    await service.create_session(
        db=db_session,
        user_id=user.id,
        expires_hours=24,
    )

    # 清理过期Session
    deleted_count = await service.cleanup_expired_sessions(db_session)
    assert deleted_count >= 1