"""
Core Dependencies 测试.

测试权限依赖注入功能.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, WebSocket, Request
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.core.deps import (
    get_current_user,
    get_current_user_ws,
    require_login,
    require_admin,
)


class TestGetCurrentUserWS:
    """测试WebSocket用户认证."""

    @pytest.mark.asyncio
    async def test_ws_auth_from_query_params(self):
        """测试从query参数获取session."""
        user_id = uuid4()
        session_id = str(uuid4())

        # Mock WebSocket
        mock_ws = MagicMock(spec=WebSocket)
        mock_ws.query_params = {"session_id": session_id}
        mock_ws.headers = {}

        # Mock Session
        mock_session = MagicMock()
        mock_session.user_id = user_id
        mock_session.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        # Mock DB
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_session)
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await get_current_user_ws(mock_ws, mock_db)

        assert result == str(user_id)

    @pytest.mark.asyncio
    async def test_ws_auth_from_headers(self):
        """测试从headers获取session."""
        user_id = uuid4()
        session_id = str(uuid4())

        # Mock WebSocket (无query参数，从headers获取)
        mock_ws = MagicMock(spec=WebSocket)
        mock_ws.query_params = {}
        mock_ws.headers = {"X-Session-ID": session_id}

        # Mock Session
        mock_session = MagicMock()
        mock_session.user_id = user_id
        mock_session.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        # Mock DB
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_session)
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await get_current_user_ws(mock_ws, mock_db)

        assert result == str(user_id)

    @pytest.mark.asyncio
    async def test_ws_auth_no_session(self):
        """测试无session返回None."""
        mock_ws = MagicMock(spec=WebSocket)
        mock_ws.query_params = {}
        mock_ws.headers = {}

        mock_db = AsyncMock()

        result = await get_current_user_ws(mock_ws, mock_db)

        assert result is None

    @pytest.mark.asyncio
    async def test_ws_auth_invalid_session(self):
        """测试无效session返回None."""
        session_id = str(uuid4())

        mock_ws = MagicMock(spec=WebSocket)
        mock_ws.query_params = {"session_id": session_id}
        mock_ws.headers = {}

        # Mock DB返回None（session不存在）
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await get_current_user_ws(mock_ws, mock_db)

        assert result is None

    @pytest.mark.asyncio
    async def test_ws_auth_expired_session(self):
        """测试过期session返回None."""
        session_id = str(uuid4())
        user_id = uuid4()

        mock_ws = MagicMock(spec=WebSocket)
        mock_ws.query_params = {"session_id": session_id}
        mock_ws.headers = {}

        # Mock Session已过期
        mock_session = MagicMock()
        mock_session.user_id = user_id
        mock_session.is_valid = True
        mock_session.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)  # 查询会过滤过期
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await get_current_user_ws(mock_ws, mock_db)

        assert result is None


class TestGetCurrentUser:
    """测试获取当前用户."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """测试成功获取用户."""
        user_id = uuid4()
        session_id = str(uuid4())

        # Mock Request
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"X-Session-ID": session_id}

        # Mock Session
        mock_session = MagicMock()
        mock_session.user_id = user_id
        mock_session.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        # Mock User
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.role = "user"

        # Mock DB
        mock_db = AsyncMock()
        session_result = MagicMock()
        session_result.scalar_one_or_none = MagicMock(return_value=mock_session)
        user_result = MagicMock()
        user_result.scalar_one_or_none = MagicMock(return_value=mock_user)

        async def execute_side_effect(*args):
            # 第一次调用返回session，第二次返回user
            call_count = mock_db.execute.call_count
            if call_count == 0:
                return session_result
            return user_result

        mock_db.execute = AsyncMock(side_effect=lambda x: session_result if mock_db.execute.call_count == 0 else user_result)

        result = await get_current_user(mock_request, mock_db)

        assert result.id == user_id

    @pytest.mark.asyncio
    async def test_get_current_user_no_session_header(self):
        """测试无session header抛出401."""
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        mock_db = AsyncMock()

        with pytest.raises(HTTPException) as exc:
            await get_current_user(mock_request, mock_db)

        assert exc.value.status_code == 401
        assert exc.value.detail == "未登录"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_session(self):
        """测试无效session抛出401."""
        session_id = str(uuid4())

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"X-Session-ID": session_id}

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(HTTPException) as exc:
            await get_current_user(mock_request, mock_db)

        assert exc.value.status_code == 401
        assert exc.value.detail == "会话已过期或无效"

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self):
        """测试用户不存在抛出401."""
        user_id = uuid4()
        session_id = str(uuid4())

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"X-Session-ID": session_id}

        # Mock Session存在
        mock_session = MagicMock()
        mock_session.user_id = user_id
        mock_session.is_valid = True
        mock_session.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        mock_db = AsyncMock()
        session_result = MagicMock()
        session_result.scalar_one_or_none = MagicMock(return_value=mock_session)
        user_result = MagicMock()
        user_result.scalar_one_or_none = MagicMock(return_value=None)

        # 第一次返回session，第二次返回None（用户不存在）
        call_count = 0
        async def execute_side_effect(*args):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return session_result
            return user_result

        mock_db.execute = AsyncMock(side_effect=execute_side_effect)

        with pytest.raises(HTTPException) as exc:
            await get_current_user(mock_request, mock_db)

        assert exc.value.status_code == 401
        assert exc.value.detail == "用户不存在"


class TestRequireLogin:
    """测试登录要求."""

    @pytest.mark.asyncio
    async def test_require_login_returns_user(self):
        """测试返回用户."""
        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.role = "user"

        result = await require_login(mock_user)

        assert result == mock_user


class TestRequireAdmin:
    """测试管理员权限要求."""

    @pytest.mark.asyncio
    async def test_require_admin_success(self):
        """测试管理员用户返回."""
        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.role = "admin"

        result = await require_admin(mock_user)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_require_admin_non_admin_raises_403(self):
        """测试非管理员抛出403."""
        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.role = "user"

        with pytest.raises(HTTPException) as exc:
            await require_admin(mock_user)

        assert exc.value.status_code == 403
        assert exc.value.detail == "需要管理员权限"