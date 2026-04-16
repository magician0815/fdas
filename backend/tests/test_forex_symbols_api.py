"""
Forex Symbols API 深度测试.

测试外汇标的管理API的授权和数据操作.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, date
from fastapi import FastAPI
from sqlalchemy import select

from app.main import app
from app.api.v1.forex_symbols import router
from app.models.user import User
from app.models.forex_symbol import ForexSymbol
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
def mock_forex_symbol():
    """Mock外汇标的."""
    symbol = MagicMock(spec=ForexSymbol)
    symbol.id = uuid4()
    symbol.code = "USDCNY"
    symbol.name = "美元人民币"
    symbol.description = "美元兑人民币汇率"
    symbol.base_currency = "USD"
    symbol.quote_currency = "CNY"
    symbol.datasource_id = uuid4()
    symbol.is_active = True
    symbol.first_trade_date = date(2020, 1, 1)
    symbol.created_at = date(2020, 1, 1)
    symbol.updated_at = date(2020, 1, 1)
    return symbol


@pytest.fixture
def mock_datasource():
    """Mock数据源."""
    ds = MagicMock(spec=DataSource)
    ds.id = uuid4()
    ds.name = "AKShare"
    ds.code = "akshare"
    ds.is_active = True
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


class TestForexSymbolsAPIAuthorized:
    """测试授权访问."""

    @pytest.mark.asyncio
    async def test_list_symbols_success(self, mock_admin_user, mock_forex_symbol):
        """测试成功列出外汇标的."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_forex_symbol]
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/api/v1/forex-symbols/")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_list_symbols_all(self, mock_admin_user, mock_forex_symbol):
        """测试列出所有外汇标的（包括禁用的）."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_forex_symbol]
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/api/v1/forex-symbols/", params={"active_only": False})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_get_symbol_success(self, mock_admin_user, mock_forex_symbol):
        """测试成功获取单个外汇标的."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_forex_symbol
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/forex-symbols/{mock_forex_symbol.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["code"] == "USDCNY"

    @pytest.mark.asyncio
    async def test_get_symbol_not_found(self, mock_admin_user):
        """测试获取不存在的外汇标的."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/forex-symbols/{uuid4()}")

        assert response.status_code == 404
        data = response.json()
        assert "外汇标的不存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_symbol_by_code_success(self, mock_admin_user, mock_forex_symbol):
        """测试成功根据代码获取外汇标的."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_forex_symbol
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/api/v1/forex-symbols/code/usdcny")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_get_symbol_by_code_not_found(self, mock_admin_user):
        """测试代码对应的外汇标的不存在."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/api/v1/forex-symbols/code/UNKNOWN")

        assert response.status_code == 404
        data = response.json()
        assert "货币对代码" in data["detail"]

    @pytest.mark.asyncio
    async def test_create_symbol_success(self, mock_admin_user, mock_datasource):
        """测试成功创建外汇标的."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        # db.add是同步方法，需要使用普通Mock
        mock_db.add = MagicMock()

        # 创建一个完整的symbol对象用于refresh返回
        created_symbol = MagicMock(spec=ForexSymbol)
        created_symbol.id = uuid4()
        created_symbol.code = "EURUSD"
        created_symbol.name = "欧元美元"
        created_symbol.description = None
        created_symbol.base_currency = None
        created_symbol.quote_currency = None
        created_symbol.datasource_id = mock_datasource.id
        created_symbol.is_active = True
        created_symbol.first_trade_date = None
        created_symbol.created_at = date(2020, 1, 1)
        created_symbol.updated_at = date(2020, 1, 1)

        # db.refresh需要更新传入的symbol对象
        async def mock_refresh(obj):
            obj.id = created_symbol.id
            obj.created_at = created_symbol.created_at
            obj.updated_at = created_symbol.updated_at
            return obj

        mock_db.refresh = mock_refresh

        # 第一次查询：检查代码是否存在（返回None）
        # 第二次查询：验证数据源（返回数据源）
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [None, mock_datasource]
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/forex-symbols/",
                json={
                    "code": "EURUSD",
                    "name": "欧元美元",
                    "datasource_id": str(mock_datasource.id)
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "外汇标的创建成功" in data["message"]

    @pytest.mark.asyncio
    async def test_create_symbol_duplicate_code(self, mock_admin_user, mock_forex_symbol):
        """测试创建重复代码的外汇标的."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_forex_symbol
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/forex-symbols/",
                json={"code": "USDCNY", "name": "美元人民币"}
            )

        assert response.status_code == 400
        data = response.json()
        assert "已存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_create_symbol_invalid_datasource(self, mock_admin_user):
        """测试创建时指定无效数据源."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        # 第一次查询：检查代码不存在（返回None）
        # 第二次查询：验证数据源不存在（返回None）
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [None, None]
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/forex-symbols/",
                json={
                    "code": "NEWCODE",
                    "name": "新货币",
                    "datasource_id": str(uuid4())
                }
            )

        assert response.status_code == 400
        data = response.json()
        assert "数据源不存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_update_symbol_success(self, mock_admin_user, mock_forex_symbol):
        """测试成功更新外汇标的."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_forex_symbol
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.put(
                f"/api/v1/forex-symbols/{mock_forex_symbol.id}",
                json={"name": "更新名称"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "外汇标的更新成功" in data["message"]

    @pytest.mark.asyncio
    async def test_update_symbol_invalid_datasource(self, mock_admin_user, mock_forex_symbol):
        """测试更新时指定无效数据源ID（覆盖行198-202）."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        # 第一次查询：获取symbol（返回symbol）
        # 第二次查询：验证数据源不存在（返回None）
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [mock_forex_symbol, None]
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.put(
                f"/api/v1/forex-symbols/{mock_forex_symbol.id}",
                json={"datasource_id": str(uuid4())}
            )

        assert response.status_code == 400
        data = response.json()
        assert "数据源不存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_update_symbol_not_found(self, mock_admin_user):
        """测试更新不存在的外汇标的."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.put(
                f"/api/v1/forex-symbols/{uuid4()}",
                json={"name": "更新名称"}
            )

        assert response.status_code == 404
        data = response.json()
        assert "外汇标的不存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_delete_symbol_success(self, mock_admin_user, mock_forex_symbol):
        """测试成功删除外汇标的."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        # 第一次查询：获取symbol
        # 第二次查询：检查关联任务
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [mock_forex_symbol, None]
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/forex-symbols/{mock_forex_symbol.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "外汇标的删除成功" in data["message"]

    @pytest.mark.asyncio
    async def test_delete_symbol_not_found(self, mock_admin_user):
        """测试删除不存在的外汇标的."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/forex-symbols/{uuid4()}")

        assert response.status_code == 404
        data = response.json()
        assert "外汇标的不存在" in data["detail"]

    @pytest.mark.asyncio
    async def test_delete_symbol_with_tasks(self, mock_admin_user, mock_forex_symbol):
        """测试删除有关联任务的外汇标的."""
        test_app = FastAPI()
        mock_db = AsyncMock()

        mock_task = MagicMock()
        # 第一次查询：获取symbol
        # 第二次查询：检查关联任务（返回一个任务）
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [mock_forex_symbol, mock_task]
        mock_db.execute.return_value = mock_result

        test_app.dependency_overrides[require_admin] = override_require_admin(mock_admin_user)
        test_app.dependency_overrides[get_db] = override_get_db(mock_db)

        test_app.include_router(router, prefix="/api/v1/forex-symbols")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/forex-symbols/{mock_forex_symbol.id}")

        assert response.status_code == 400
        data = response.json()
        assert "关联的采集任务" in data["detail"]


# =====================
# Unauthorized Tests
# =====================

class TestForexSymbolsAPIUnauthorized:
    """测试未授权访问."""

    @pytest.mark.asyncio
    async def test_list_symbols_unauthorized(self):
        """测试未授权列出外汇标的."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/forex-symbols/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_symbol_unauthorized(self):
        """测试未授权获取外汇标的."""
        symbol_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/forex-symbols/{symbol_id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_symbol_by_code_unauthorized(self):
        """测试未授权按代码获取外汇标的."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/forex-symbols/code/USDCNY")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_symbol_unauthorized(self):
        """测试未授权创建外汇标的."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/forex-symbols/",
                json={"code": "EURUSD", "name": "欧元美元"}
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_symbol_unauthorized(self):
        """测试未授权更新外汇标的."""
        symbol_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(
                f"/api/v1/forex-symbols/{symbol_id}",
                json={"name": "新名称"}
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_symbol_unauthorized(self):
        """测试未授权删除外汇标的."""
        symbol_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.delete(f"/api/v1/forex-symbols/{symbol_id}")

        assert response.status_code == 401


# =====================
# Parameter Validation Tests
# =====================

class TestForexSymbolsAPIParams:
    """测试参数验证."""

    @pytest.mark.asyncio
    async def test_get_symbol_invalid_uuid(self):
        """测试无效UUID格式."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/forex-symbols/not-a-uuid")

        # 401 (auth first) or 422 (validation)
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_list_symbols_with_params_unauthorized(self):
        """测试带参数但未授权."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/forex-symbols/",
                params={"active_only": False}
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_symbol_empty_code_unauthorized(self):
        """测试创建空代码（未授权）."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/forex-symbols/",
                json={"code": "", "name": "测试"}
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_symbol_partial_data_unauthorized(self):
        """测试部分更新数据（未授权）."""
        symbol_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(
                f"/api/v1/forex-symbols/{symbol_id}",
                json={"is_active": False}
            )

        assert response.status_code == 401


# =====================
# Response Format Tests
# =====================

class TestForexSymbolsAPIResponseFormat:
    """测试响应格式."""

    @pytest.mark.asyncio
    async def test_unauthorized_response_format(self):
        """测试未授权响应格式."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/forex-symbols/")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_invalid_uuid_response_format(self):
        """测试无效UUID响应格式."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/forex-symbols/invalid")

        if response.status_code == 422:
            data = response.json()
            assert "detail" in data