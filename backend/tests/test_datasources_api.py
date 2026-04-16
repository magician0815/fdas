"""
Datasources API tests.

Tests for datasource management API endpoints.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, date
from fastapi import FastAPI

from app.main import app
from app.api.v1.datasources import router
from app.models.user import User
from app.models.datasource import DataSource
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
def mock_datasource():
    """Mock数据源."""
    ds = MagicMock(spec=DataSource)
    ds.id = uuid4()
    ds.name = "AKShare"
    ds.market_id = None
    ds.interface = "forex_hist"
    ds.description = "AKShare外汇数据源"
    ds.config_schema = {"type": "object"}
    ds.supported_symbols = ["USDCNY", "EURUSD"]
    ds.min_date = date(2020, 1, 1)
    ds.type = "akshare"
    ds.is_active = True
    ds.created_at = date(2020, 1, 1)
    ds.updated_at = date(2020, 1, 1)
    return ds


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


class TestDatasourcesAPIAuthorized:
    """测试授权访问."""

    @pytest.mark.asyncio
    async def test_list_datasources_success(self, mock_admin_user, mock_datasource):
        """测试成功列出数据源."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_datasource]
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/datasources")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/api/v1/datasources/")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_list_datasources_empty(self, mock_admin_user):
        """测试空数据源列表."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/datasources")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/api/v1/datasources/")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 0

    @pytest.mark.asyncio
    async def test_get_datasource_success(self, mock_admin_user, mock_datasource):
        """测试成功获取单个数据源."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_datasource
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/datasources")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/datasources/{mock_datasource.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "AKShare"

    @pytest.mark.asyncio
    async def test_get_datasource_not_found(self, mock_admin_user):
        """测试获取不存在的数据源."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/datasources")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/datasources/{uuid4()}")

        assert response.status_code == 404
        data = response.json()
        assert "数据源不存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_create_datasource_success(self, mock_admin_user):
        """测试成功创建数据源."""
        test_app = FastAPI()
        mock_db = AsyncMock()
        mock_db.add = MagicMock()

        # 创建完整的数据源对象用于refresh返回
        created_ds = MagicMock(spec=DataSource)
        created_ds.id = uuid4()
        created_ds.name = "NewDatasource"
        created_ds.market_id = None
        created_ds.interface = "test_interface"
        created_ds.description = "测试数据源"
        created_ds.config_schema = {"type": "object"}
        created_ds.supported_symbols = None
        created_ds.min_date = None
        created_ds.type = "akshare"
        created_ds.is_active = True
        created_ds.created_at = date(2020, 1, 1)
        created_ds.updated_at = date(2020, 1, 1)

        async def mock_refresh(obj):
            obj.id = created_ds.id
            obj.created_at = created_ds.created_at
            obj.updated_at = created_ds.updated_at
            return obj

        mock_db.refresh = mock_refresh

        # 第一次查询：检查名称不存在（返回None）
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/datasources")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/datasources/",
                json={
                    "name": "NewDatasource",
                    "interface": "test_interface",
                    "config_schema": {"type": "object"}
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "数据源创建成功" in data["message"]

    @pytest.mark.asyncio
    async def test_create_datasource_duplicate_name(self, mock_admin_user, mock_datasource):
        """测试创建重复名称的数据源."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_datasource
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/datasources")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/datasources/",
                json={
                    "name": "AKShare",
                    "interface": "test_interface",
                    "config_schema": {"type": "object"}
                }
            )

        assert response.status_code == 400
        data = response.json()
        assert "数据源名称已存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_update_datasource_success(self, mock_admin_user, mock_datasource):
        """测试成功更新数据源."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_datasource
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/datasources")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.put(
                f"/api/v1/datasources/{mock_datasource.id}",
                json={"name": "UpdatedName"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "数据源更新成功" in data["message"]

    @pytest.mark.asyncio
    async def test_update_datasource_not_found(self, mock_admin_user):
        """测试更新不存在的数据源."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/datasources")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.put(
                f"/api/v1/datasources/{uuid4()}",
                json={"name": "UpdatedName"}
            )

        assert response.status_code == 404
        data = response.json()
        assert "数据源不存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_delete_datasource_success(self, mock_admin_user, mock_datasource):
        """测试成功删除数据源."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_datasource
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/datasources")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/datasources/{mock_datasource.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "数据源删除成功" in data["message"]

    @pytest.mark.asyncio
    async def test_delete_datasource_not_found(self, mock_admin_user):
        """测试删除不存在的数据源."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/datasources")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/datasources/{uuid4()}")

        assert response.status_code == 404
        data = response.json()
        assert "数据源不存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_supported_symbols_success(self, mock_admin_user, mock_datasource):
        """测试成功获取支持的货币对."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_datasource
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        # Mock akshare_collector
        mock_symbols = [{"value": "美元人民币", "code": "USDCNY", "label": "美元人民币"}]
        with patch('app.collectors.akshare_collector.akshare_collector.fetch_supported_symbols', return_value=mock_symbols):
            test_app.include_router(router, prefix="/api/v1/datasources")

            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
                response = await client.get(f"/api/v1/datasources/{mock_datasource.id}/symbols")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "symbols" in data["data"]

    @pytest.mark.asyncio
    async def test_get_supported_symbols_not_found(self, mock_admin_user):
        """测试获取不存在的数据源的货币对."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/datasources")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/datasources/{uuid4()}/symbols")

        assert response.status_code == 404
        data = response.json()
        assert "数据源不存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_fetch_and_compare_symbols_success(self, mock_admin_user, mock_datasource):
        """测试成功获取并比较货币对."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_datasource
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        # Mock akshare_collector返回新货币对列表
        mock_symbols = [
            {"value": "美元人民币", "code": "USDCNY", "label": "美元人民币"},
            {"value": "欧元美元", "code": "EURUSD", "label": "欧元美元"},
            {"value": "英镑美元", "code": "GBPUSD", "label": "英镑美元"}  # 新增的
        ]
        with patch('app.collectors.akshare_collector.akshare_collector.fetch_supported_symbols', return_value=mock_symbols):
            test_app.include_router(router, prefix="/api/v1/datasources")

            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
                response = await client.post(f"/api/v1/datasources/{mock_datasource.id}/symbols/fetch")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "has_changes" in data["data"]
        assert len(data["data"]["added"]) > 0  # GBPUSD是新增的

    @pytest.mark.asyncio
    async def test_fetch_and_compare_symbols_not_found(self, mock_admin_user):
        """测试获取不存在的数据源的货币对变更."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/datasources")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.post(f"/api/v1/datasources/{uuid4()}/symbols/fetch")

        assert response.status_code == 404
        data = response.json()
        assert "数据源不存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_update_supported_symbols_success(self, mock_admin_user, mock_datasource):
        """测试成功更新支持的货币对."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_datasource
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        mock_symbols = [
            {"value": "美元人民币", "code": "USDCNY", "label": "美元人民币"},
            {"value": "欧元美元", "code": "EURUSD", "label": "欧元美元"}
        ]
        with patch('app.collectors.akshare_collector.akshare_collector.fetch_supported_symbols', return_value=mock_symbols):
            test_app.include_router(router, prefix="/api/v1/datasources")

            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
                response = await client.put(f"/api/v1/datasources/{mock_datasource.id}/symbols")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "成功更新" in data["message"]

    @pytest.mark.asyncio
    async def test_update_supported_symbols_not_found(self, mock_admin_user):
        """测试更新不存在的数据源的货币对."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/datasources")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.put(f"/api/v1/datasources/{uuid4()}/symbols")

        assert response.status_code == 404
        data = response.json()
        assert "数据源不存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_sync_symbols_to_database_success(self, mock_admin_user, mock_datasource):
        """测试成功同步货币对到数据库."""
        test_app = FastAPI()
        mock_db = AsyncMock()
        mock_db.add = MagicMock()

        mock_result = MagicMock()
        # 第一次查询：获取datasource
        # 后续查询：检查每个symbol是否存在（全部返回None表示新增）
        mock_result.scalar_one_or_none.side_effect = [mock_datasource, None, None, None]
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        mock_symbols = [
            {"value": "美元人民币", "code": "USDCNY", "label": "美元人民币"},
            {"value": "欧元美元", "code": "EURUSD", "label": "欧元美元"}
        ]
        with patch('app.collectors.akshare_collector.akshare_collector.fetch_supported_symbols', return_value=mock_symbols):
            test_app.include_router(router, prefix="/api/v1/datasources")

            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
                response = await client.post(f"/api/v1/datasources/{mock_datasource.id}/sync-to-database")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "同步完成" in data["message"]

    @pytest.mark.asyncio
    async def test_sync_symbols_to_database_existing_same_name(self, mock_admin_user, mock_datasource):
        """测试同步时symbol已存在且名称相同（跳过计数，覆盖行361-365）."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        # 创建已存在的symbol，名称与fetch返回的相同
        existing_symbol = MagicMock()
        existing_symbol.name = "美元人民币"  # 名称相同

        # 第一次查询：获取datasource
        # 后续查询：检查每个symbol是否存在（返回existing_symbol表示存在）
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [mock_datasource, existing_symbol, existing_symbol]
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        # fetch返回的symbol名称与existing_symbol相同
        mock_symbols = [
            {"value": "美元人民币", "code": "USDCNY", "label": "美元人民币"},
            {"value": "欧元美元", "code": "EURUSD", "label": "欧元美元"}
        ]
        with patch('app.collectors.akshare_collector.akshare_collector.fetch_supported_symbols', return_value=mock_symbols):
            test_app.include_router(router, prefix="/api/v1/datasources")

            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
                response = await client.post(f"/api/v1/datasources/{mock_datasource.id}/sync-to-database")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # 第一个symbol名称相同跳过，第二个名称不同触发更新
        assert data["data"]["skipped"] == 1
        assert data["data"]["updated"] == 1

    @pytest.mark.asyncio
    async def test_sync_symbols_to_database_not_found(self, mock_admin_user):
        """测试同步不存在的数据源的货币对."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/datasources")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.post(f"/api/v1/datasources/{uuid4()}/sync-to-database")

        assert response.status_code == 404
        data = response.json()
        assert "数据源不存在" in data["detail"]


# =====================
# Unauthorized Tests
# =====================

class TestDatasourcesAPIUnauthorized:
    """Test unauthorized access to datasources API."""

    @pytest.mark.asyncio
    async def test_list_datasources_unauthorized(self):
        """Test list datasources without authentication."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/datasources/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_datasource_unauthorized(self):
        """Test get datasource without authentication."""
        datasource_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/datasources/{datasource_id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_datasource_unauthorized(self):
        """Test create datasource without authentication."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/datasources/", json={})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_datasource_unauthorized(self):
        """Test update datasource without authentication."""
        datasource_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(f"/api/v1/datasources/{datasource_id}", json={})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_datasource_unauthorized(self):
        """Test delete datasource without authentication."""
        datasource_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.delete(f"/api/v1/datasources/{datasource_id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_supported_symbols_unauthorized(self):
        """Test get supported symbols without authentication."""
        datasource_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/datasources/{datasource_id}/symbols")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_fetch_compare_symbols_unauthorized(self):
        """Test fetch and compare symbols without authentication."""
        datasource_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(f"/api/v1/datasources/{datasource_id}/symbols/fetch")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_supported_symbols_unauthorized(self):
        """Test update supported symbols without authentication."""
        datasource_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(f"/api/v1/datasources/{datasource_id}/symbols")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_sync_symbols_to_database_unauthorized(self):
        """Test sync symbols to database without authentication."""
        datasource_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(f"/api/v1/datasources/{datasource_id}/sync-to-database")

        assert response.status_code == 401


# =====================
# Parameter Validation Tests
# =====================

class TestDatasourcesAPIParams:
    """Test parameter validation."""

    @pytest.mark.asyncio
    async def test_get_datasource_invalid_uuid(self):
        """Test get datasource with invalid UUID."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/datasources/not-a-uuid")

        # Should return 401 (auth check first) or 422 (validation)
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_delete_datasource_invalid_uuid(self):
        """Test delete datasource with invalid UUID."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.delete("/api/v1/datasources/not-a-uuid")

        assert response.status_code in [401, 422]


# =====================
# Response Format Tests
# =====================

class TestDatasourcesAPIResponseFormat:
    """Test response format."""

    @pytest.mark.asyncio
    async def test_unauthorized_response_format(self):
        """Test unauthorized response format."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/datasources/")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data