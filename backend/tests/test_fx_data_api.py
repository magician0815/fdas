"""
FX Data API tests.

Tests for forex daily data API endpoints.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import date, timedelta
from fastapi import FastAPI

from app.api.v1.fx_data import router, ForexDailyItem
from app.models.user import User
from app.models.forex_daily import ForexDaily
from app.services.forex_daily_service import forex_daily_service
from app.services.period_aggregation_service import PeriodAggregationService


@pytest.fixture
def mock_user():
    """Mock用户."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.username = "testuser"
    return user


@pytest.fixture
def mock_forex_daily():
    """Mock外汇日线数据."""
    daily = MagicMock(spec=ForexDaily)
    daily.id = uuid4()
    daily.symbol_id = uuid4()
    daily.date = date.today()
    daily.open = 7.2
    daily.high = 7.25
    daily.low = 7.15
    daily.close = 7.22
    daily.change_pct = 0.28
    daily.change_amount = 0.02
    daily.amplitude = 1.39
    return daily


def override_require_login(mock_user):
    """覆盖require_login依赖."""
    async def _require_login():
        return mock_user
    return _require_login


def override_get_db(mock_db):
    """覆盖get_db依赖."""
    async def _get_db():
        return mock_db
    return _get_db


class TestForexDailyItem:
    """测试ForexDailyItem类."""

    def test_init_with_all_fields(self, mock_forex_daily):
        """测试完整数据初始化."""
        item = ForexDailyItem(mock_forex_daily)
        assert item.id == str(mock_forex_daily.id)
        assert item.symbol_id == str(mock_forex_daily.symbol_id)
        assert item.date == str(mock_forex_daily.date)
        assert item.open == 7.2
        assert item.high == 7.25
        assert item.low == 7.15
        assert item.close == 7.22

    def test_init_with_none_fields(self):
        """测试None字段处理."""
        daily = MagicMock(spec=ForexDaily)
        daily.id = uuid4()
        daily.symbol_id = uuid4()
        daily.date = date.today()
        daily.open = None
        daily.high = None
        daily.low = None
        daily.close = None
        daily.change_pct = None
        daily.change_amount = None
        daily.amplitude = None

        item = ForexDailyItem(daily)
        assert item.open is None
        assert item.high is None
        assert item.low is None
        assert item.close is None

    def test_to_dict(self, mock_forex_daily):
        """测试转换为字典."""
        item = ForexDailyItem(mock_forex_daily)
        d = item.to_dict()
        assert "id" in d
        assert "symbol_id" in d
        assert "date" in d
        assert "open" in d
        assert "close" in d


class TestGetFXData:
    """测试获取外汇数据API."""

    @pytest.mark.asyncio
    async def test_get_fx_data_daily_success(self, mock_user, mock_forex_daily):
        """测试获取日线数据成功."""
        app = FastAPI()
        mock_db = AsyncMock()

        from app.api.v1.fx_data import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        # Mock服务返回
        with patch.object(forex_daily_service, 'get_forex_daily_asc', return_value=[mock_forex_daily]):
            app.include_router(router, prefix="/api/v1/fx")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/fx/data",
                    params={"symbol_code": "USDCNY", "period": "daily"}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    @pytest.mark.asyncio
    async def test_get_fx_data_weekly_success(self, mock_user, mock_forex_daily):
        """测试获取周线数据成功."""
        app = FastAPI()
        mock_db = AsyncMock()

        # 创建多天数据用于周线聚合
        daily_list = []
        for i in range(10):
            d = MagicMock(spec=ForexDaily)
            d.id = uuid4()
            d.symbol_id = uuid4()
            d.date = date.today() - timedelta(days=i)
            d.open = 7.0 + i * 0.02
            d.high = 7.05 + i * 0.02
            d.low = 6.95 + i * 0.02
            d.close = 7.0 + i * 0.02
            d.change_pct = 0.1
            d.change_amount = 0.01
            d.amplitude = 1.0
            daily_list.append(d)

        from app.api.v1.fx_data import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(forex_daily_service, 'get_forex_daily_asc', return_value=daily_list):
            app.include_router(router, prefix="/api/v1/fx")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/fx/data",
                    params={"symbol_code": "USDCNY", "period": "weekly"}
                )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_fx_data_monthly_success(self, mock_user, mock_forex_daily):
        """测试获取月线数据成功."""
        app = FastAPI()
        mock_db = AsyncMock()

        # 创建多天数据用于月线聚合
        daily_list = []
        for i in range(30):
            d = MagicMock(spec=ForexDaily)
            d.id = uuid4()
            d.symbol_id = uuid4()
            d.date = date.today() - timedelta(days=i)
            d.open = 7.0 + i * 0.01
            d.high = 7.05 + i * 0.01
            d.low = 6.95 + i * 0.01
            d.close = 7.0 + i * 0.01
            d.change_pct = 0.1
            d.change_amount = 0.01
            d.amplitude = 1.0
            daily_list.append(d)

        from app.api.v1.fx_data import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(forex_daily_service, 'get_forex_daily_asc', return_value=daily_list):
            app.include_router(router, prefix="/api/v1/fx")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/fx/data",
                    params={"symbol_code": "USDCNY", "period": "monthly"}
                )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_fx_data_empty_result(self, mock_user):
        """测试空结果返回."""
        app = FastAPI()
        mock_db = AsyncMock()

        from app.api.v1.fx_data import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(forex_daily_service, 'get_forex_daily_asc', return_value=[]):
            app.include_router(router, prefix="/api/v1/fx")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/fx/data")

            assert response.status_code == 200
            data = response.json()
            assert len(data["data"]) == 0

    @pytest.mark.asyncio
    async def test_get_fx_data_with_custom_dates(self, mock_user, mock_forex_daily):
        """测试自定义日期范围."""
        app = FastAPI()
        mock_db = AsyncMock()

        from app.api.v1.fx_data import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        start = date.today() - timedelta(days=10)
        end = date.today()

        with patch.object(forex_daily_service, 'get_forex_daily_asc', return_value=[mock_forex_daily]):
            app.include_router(router, prefix="/api/v1/fx")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/fx/data",
                    params={
                        "symbol_code": "USDCNY",
                        "start_date": start.isoformat(),
                        "end_date": end.isoformat()
                    }
                )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_fx_data_invalid_period(self, mock_user, mock_forex_daily):
        """测试无效period参数处理（覆盖else分支）."""
        app = FastAPI()
        mock_db = AsyncMock()

        from app.api.v1.fx_data import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(forex_daily_service, 'get_forex_daily_asc', return_value=[mock_forex_daily]):
            app.include_router(router, prefix="/api/v1/fx")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/fx/data",
                    params={"symbol_code": "USDCNY", "period": "invalid_period"}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            # 无效period会fallback到daily处理


class TestGetFXDataById:
    """测试根据ID获取数据API."""

    @pytest.mark.asyncio
    async def test_get_fx_data_by_id_success(self, mock_user, mock_forex_daily):
        """测试根据ID获取成功."""
        app = FastAPI()
        mock_db = AsyncMock()
        symbol_id = uuid4()

        mock_forex_daily.symbol_id = symbol_id

        from app.api.v1.fx_data import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(forex_daily_service, 'get_forex_daily', return_value=[mock_forex_daily]):
            app.include_router(router, prefix="/api/v1/fx")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(f"/api/v1/fx/data/{symbol_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    @pytest.mark.asyncio
    async def test_get_fx_data_by_id_with_dates(self, mock_user, mock_forex_daily):
        """测试根据ID和日期获取."""
        app = FastAPI()
        mock_db = AsyncMock()
        symbol_id = uuid4()

        from app.api.v1.fx_data import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        start = date.today() - timedelta(days=10)

        with patch.object(forex_daily_service, 'get_forex_daily', return_value=[mock_forex_daily]):
            app.include_router(router, prefix="/api/v1/fx")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/v1/fx/data/{symbol_id}",
                    params={"start_date": start.isoformat()}
                )

            assert response.status_code == 200


class TestGetIndicators:
    """测试获取技术指标API."""

    @pytest.mark.asyncio
    async def test_get_indicators_daily_success(self, mock_user, mock_forex_daily):
        """测试获取日线指标成功."""
        app = FastAPI()
        mock_db = AsyncMock()

        # 创建足够数据用于指标计算
        daily_list = []
        for i in range(100):
            d = MagicMock(spec=ForexDaily)
            d.id = uuid4()
            d.symbol_id = uuid4()
            d.date = date.today() - timedelta(days=i)
            d.open = 7.0 + i * 0.01
            d.high = 7.05 + i * 0.01
            d.low = 6.95 + i * 0.01
            d.close = 7.0 + i * 0.01
            d.change_pct = 0.1
            d.change_amount = 0.01
            d.amplitude = 1.0
            daily_list.append(d)

        from app.api.v1.fx_data import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(forex_daily_service, 'get_forex_daily_asc', return_value=daily_list):
            app.include_router(router, prefix="/api/v1/fx")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/fx/indicators",
                    params={"symbol_code": "USDCNY", "period": "daily"}
                )

            assert response.status_code == 200
            data = response.json()
            assert "ma" in data["data"]
            assert "macd" in data["data"]

    @pytest.mark.asyncio
    async def test_get_indicators_weekly_success(self, mock_user, mock_forex_daily):
        """测试获取周线指标成功."""
        app = FastAPI()
        mock_db = AsyncMock()

        # 创建足够数据用于周线指标计算
        daily_list = []
        for i in range(365):
            d = MagicMock(spec=ForexDaily)
            d.id = uuid4()
            d.symbol_id = uuid4()
            d.date = date.today() - timedelta(days=i)
            d.open = 7.0 + i * 0.001
            d.high = 7.05 + i * 0.001
            d.low = 6.95 + i * 0.001
            d.close = 7.0 + i * 0.001
            d.change_pct = 0.01
            d.change_amount = 0.001
            d.amplitude = 0.1
            daily_list.append(d)

        from app.api.v1.fx_data import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(forex_daily_service, 'get_forex_daily_asc', return_value=daily_list):
            app.include_router(router, prefix="/api/v1/fx")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/fx/indicators",
                    params={"symbol_code": "USDCNY", "period": "weekly"}
                )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_indicators_monthly_success(self, mock_user, mock_forex_daily):
        """测试获取月线指标成功."""
        app = FastAPI()
        mock_db = AsyncMock()

        # 创建足够数据用于月线指标计算
        daily_list = []
        for i in range(730):
            d = MagicMock(spec=ForexDaily)
            d.id = uuid4()
            d.symbol_id = uuid4()
            d.date = date.today() - timedelta(days=i)
            d.open = 7.0 + i * 0.0001
            d.high = 7.05 + i * 0.0001
            d.low = 6.95 + i * 0.0001
            d.close = 7.0 + i * 0.0001
            d.change_pct = 0.001
            d.change_amount = 0.0001
            d.amplitude = 0.01
            daily_list.append(d)

        from app.api.v1.fx_data import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(forex_daily_service, 'get_forex_daily_asc', return_value=daily_list):
            app.include_router(router, prefix="/api/v1/fx")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/fx/indicators",
                    params={"symbol_code": "USDCNY", "period": "monthly"}
                )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_indicators_empty_result(self, mock_user):
        """测试空结果返回默认结构."""
        app = FastAPI()
        mock_db = AsyncMock()

        from app.api.v1.fx_data import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(forex_daily_service, 'get_forex_daily_asc', return_value=[]):
            app.include_router(router, prefix="/api/v1/fx")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/fx/indicators")

            assert response.status_code == 200
            data = response.json()
            assert "ma" in data["data"]
            assert "macd" in data["data"]

    @pytest.mark.asyncio
    async def test_get_indicators_invalid_period(self, mock_user, mock_forex_daily):
        """测试无效period参数处理（覆盖else分支）."""
        app = FastAPI()
        mock_db = AsyncMock()

        daily_list = []
        for i in range(100):
            d = MagicMock(spec=ForexDaily)
            d.id = uuid4()
            d.symbol_id = uuid4()
            d.date = date.today() - timedelta(days=i)
            d.open = 7.0 + i * 0.01
            d.high = 7.05 + i * 0.01
            d.low = 6.95 + i * 0.01
            d.close = 7.0 + i * 0.01
            d.change_pct = 0.1
            d.change_amount = 0.01
            d.amplitude = 1.0
            daily_list.append(d)

        from app.api.v1.fx_data import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(forex_daily_service, 'get_forex_daily_asc', return_value=daily_list):
            app.include_router(router, prefix="/api/v1/fx")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/fx/indicators",
                    params={"symbol_code": "USDCNY", "period": "invalid_period"}
                )

            assert response.status_code == 200


# =====================
# Unauthorized Tests
# =====================

class TestFXDataAPIUnauthorized:
    """Test unauthorized access to FX data API."""

    @pytest.mark.asyncio
    async def test_get_fx_data_unauthorized(self):
        """Test get FX data without authentication."""
        from app.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/fx/data")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_fx_data_by_id_unauthorized(self):
        """Test get FX data by ID without authentication."""
        from app.main import app
        symbol_id = str(uuid4())

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/fx/data/{symbol_id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_indicators_unauthorized(self):
        """Test get indicators without authentication."""
        from app.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/fx/indicators")

        assert response.status_code == 401