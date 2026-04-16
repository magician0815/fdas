"""
Users API tests.

Tests for user management API endpoints - focusing on unauthorized cases.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime
from fastapi import FastAPI

from app.main import app
from app.api.v1.users import router
from app.models.user import User
from app.core.deps import require_admin
from app.core.database import get_db
from app.services.user_service import UserService


@pytest.fixture
def mock_admin_user():
    """Mock admin用户."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.username = "admin"
    user.role = "admin"
    return user


@pytest.fixture
def mock_user():
    """Mock普通用户."""
    user_id = uuid4()
    user = MagicMock(spec=User)
    user.id = str(user_id)  # 返回字符串类型以匹配UserResponse
    user.username = "testuser"
    user.role = "user"
    user.created_at = datetime.now()
    user.updated_at = datetime.now()
    return user


def override_require_admin(mock_user):
    """覆盖require_admin依赖."""
    async def _require_admin():
        return mock_user
    return _require_admin


def override_get_db(mock_db):
    """覆盖get_db依赖."""
    async def _get_db():
        return mock_db
    return _get_db


class TestUsersAPIAuthorized:
    """测试授权访问."""

    @pytest.mark.asyncio
    async def test_list_users_success(self, mock_admin_user, mock_user):
        """测试成功列出用户."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(UserService, 'get_users', return_value=[mock_user]):
            test_app.include_router(router, prefix="/api/v1/users")

            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
                response = await client.get("/api/v1/users/")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_list_users_empty(self, mock_admin_user):
        """测试空用户列表."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(UserService, 'get_users', return_value=[]):
            test_app.include_router(router, prefix="/api/v1/users")

            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
                response = await client.get("/api/v1/users/")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 0

    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_admin_user, mock_user):
        """测试成功创建用户."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(UserService, 'create_user', return_value=mock_user):
            test_app.include_router(router, prefix="/api/v1/users")

            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/users/",
                    json={"username": "newuser", "password": "pass123", "role": "user"}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "用户创建成功" in data["message"]

    @pytest.mark.asyncio
    async def test_update_user_success(self, mock_admin_user, mock_user):
        """测试成功更新用户."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(UserService, 'update_user', return_value=mock_user):
            test_app.include_router(router, prefix="/api/v1/users")

            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
                response = await client.put(
                    f"/api/v1/users/{mock_user.id}",
                    json={"username": "updateduser"}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "用户更新成功" in data["message"]

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, mock_admin_user):
        """测试更新不存在的用户."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(UserService, 'update_user', return_value=None):
            test_app.include_router(router, prefix="/api/v1/users")

            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
                response = await client.put(
                    f"/api/v1/users/{uuid4()}",
                    json={"username": "updateduser"}
                )

            assert response.status_code == 404
            data = response.json()
            assert "用户不存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_delete_user_success(self, mock_admin_user):
        """测试成功删除用户."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(UserService, 'delete_user', return_value=True):
            test_app.include_router(router, prefix="/api/v1/users")

            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
                response = await client.delete(f"/api/v1/users/{uuid4()}")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "用户删除成功" in data["message"]

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, mock_admin_user):
        """测试删除不存在的用户."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(UserService, 'delete_user', return_value=False):
            test_app.include_router(router, prefix="/api/v1/users")

            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
                response = await client.delete(f"/api/v1/users/{uuid4()}")

            assert response.status_code == 404
            data = response.json()
            assert "用户不存在" in data["detail"]


# =====================
# Unauthorized Tests - These don't require mocking
# =====================

class TestUsersAPIUnauthorized:
    """Test unauthorized access to users API."""

    @pytest.mark.asyncio
    async def test_list_users_unauthorized(self):
        """Test list users without authentication."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/users/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_user_unauthorized(self):
        """Test create user without authentication."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/users/", json={})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_user_unauthorized(self):
        """Test update user without authentication."""
        user_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(f"/api/v1/users/{user_id}", json={})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_user_unauthorized(self):
        """Test delete user without authentication."""
        user_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.delete(f"/api/v1/users/{user_id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_users_no_session_header(self):
        """Test list users without session header."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/users/")

        # Should return 401 (no session)
        assert response.status_code == 401


# =====================
# Response Format Tests
# =====================

class TestUsersAPIResponseFormat:
    """Test response format when unauthorized."""

    @pytest.mark.asyncio
    async def test_unauthorized_response_format(self):
        """Test unauthorized response format."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/users/")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data