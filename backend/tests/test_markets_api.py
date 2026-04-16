"""
Markets API 测试.

测试市场类型管理API.

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
from app.api.v1.markets import router
from app.models.user import User
from app.models.market import Market
from app.core.deps import require_admin
from app.core.database import get_db


@pytest.fixture
def mock_admin_user():
    """Mock admin用户."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.username = "admin"
    user.role = "admin"
    return user


@pytest.fixture
def mock_market():
    """Mock市场类型."""
    market = MagicMock(spec=Market)
    market.id = uuid4()
    market.code = "forex"
    market.name = "外汇市场"
    market.description = "外汇交易市场"
    market.timezone = "Asia/Shanghai"
    market.is_active = True
    market.created_at = datetime.now()
    market.updated_at = datetime.now()
    return market


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


class TestMarketsAPIAuthorized:
    """测试授权访问."""

    @pytest.mark.asyncio
    async def test_list_markets_success(self, mock_admin_user, mock_market):
        """测试成功列出活跃市场."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        # Mock数据库查询结果
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_market]
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/markets")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/api/v1/markets/")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_list_markets_empty(self, mock_admin_user):
        """测试空市场列表."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/markets")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/api/v1/markets/")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 0

    @pytest.mark.asyncio
    async def test_list_all_markets_success(self, mock_admin_user, mock_market):
        """测试成功列出所有市场."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        # 创建一个禁用的市场
        inactive_market = MagicMock(spec=Market)
        inactive_market.id = uuid4()
        inactive_market.code = "crypto"
        inactive_market.name = "加密货币"
        inactive_market.description = "加密货币市场"
        inactive_market.timezone = "UTC"
        inactive_market.is_active = False
        inactive_market.created_at = datetime.now()
        inactive_market.updated_at = datetime.now()

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_market, inactive_market]
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/markets")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/api/v1/markets/all")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2

    @pytest.mark.asyncio
    async def test_get_market_success(self, mock_admin_user, mock_market):
        """测试成功获取单个市场."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_market
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/markets")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/markets/{mock_market.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["code"] == "forex"

    @pytest.mark.asyncio
    async def test_get_market_invalid_uuid(self, mock_admin_user):
        """测试无效UUID格式."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/markets")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/api/v1/markets/invalid-uuid")

        assert response.status_code == 400
        data = response.json()
        assert "无效的市场ID格式" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_market_not_found(self, mock_admin_user):
        """测试市场不存在."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/markets")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/markets/{uuid4()}")

        assert response.status_code == 404
        data = response.json()
        assert "市场类型不存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_market_by_code_success(self, mock_admin_user, mock_market):
        """测试成功根据代码获取市场."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_market
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/markets")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/api/v1/markets/code/forex")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["code"] == "forex"

    @pytest.mark.asyncio
    async def test_get_market_by_code_not_found(self, mock_admin_user):
        """测试代码对应市场不存在."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/markets")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/api/v1/markets/code/unknown")

        assert response.status_code == 404
        data = response.json()
        assert "市场代码" in data["detail"]


class TestMarketsAPIUnauthorized:
    """测试未授权访问."""

    @pytest.mark.asyncio
    async def test_list_markets_unauthorized(self):
        """测试未授权列出市场."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/markets/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_all_markets_unauthorized(self):
        """测试未授权列出所有市场."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/markets/all")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_market_unauthorized(self):
        """测试未授权获取市场."""
        market_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/markets/{market_id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_market_by_code_unauthorized(self):
        """测试未授权按代码获取市场."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/markets/code/forex")

        assert response.status_code == 401


class TestMarketsAPIParams:
    """测试参数验证."""

    @pytest.mark.asyncio
    async def test_get_market_invalid_uuid(self):
        """测试无效UUID格式."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/markets/invalid-uuid")

        assert response.status_code in [401, 400, 422]

    @pytest.mark.asyncio
    async def test_get_market_by_code_empty_unauthorized(self):
        """测试空代码（未授权，返回重定向或404）."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/markets/code/")

        # 307 redirect or 401 (auth) or 404/405
        assert response.status_code in [307, 401, 404, 405]


class TestMarketsAPIResponseFormat:
    """测试响应格式."""

    @pytest.mark.asyncio
    async def test_unauthorized_response_format(self):
        """测试未授权响应格式."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/markets/")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data