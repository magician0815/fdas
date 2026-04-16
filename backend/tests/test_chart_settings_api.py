"""
用户图表设置API测试.

测试chart_settings.py API路由.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.api.v1.chart_settings import router
from app.models.user import User
from app.models.user_chart_setting import UserChartSetting


@pytest.fixture
def mock_user():
    """Mock用户."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.username = "testuser"
    return user


@pytest.fixture
def mock_setting():
    """Mock图表设置."""
    setting = MagicMock(spec=UserChartSetting)
    setting.id = uuid4()
    setting.user_id = uuid4()
    setting.setting_type = "chart_config"
    setting.setting_key = "symbol_001"
    setting.setting_value = {"ma_periods": [5, 10, 20]}
    setting.updated_at = datetime.now(timezone.utc)
    return setting


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


class TestGetChartSettings:
    """测试获取图表设置."""

    @pytest.mark.asyncio
    async def test_get_all_settings(self, mock_user, mock_setting):
        """测试获取所有设置."""
        app = FastAPI()
        mock_db = AsyncMock()

        # Mock查询结果
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = [mock_setting]
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.api.v1.chart_settings import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        app.include_router(router, prefix="/api/v1")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/settings")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_get_settings_by_type(self, mock_user, mock_setting):
        """测试获取指定类型设置."""
        app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalars().all.return_value = [mock_setting]
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.api.v1.chart_settings import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        app.include_router(router, prefix="/api/v1")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/settings?setting_type=chart_config")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_get_settings_empty(self, mock_user):
        """测试获取空设置."""
        app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalars().all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.api.v1.chart_settings import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        app.include_router(router, prefix="/api/v1")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/settings")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 0


class TestGetChartSetting:
    """测试获取单个设置."""

    @pytest.mark.asyncio
    async def test_get_setting_found(self, mock_user, mock_setting):
        """测试获取存在的设置."""
        app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_setting
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.api.v1.chart_settings import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        app.include_router(router, prefix="/api/v1")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/settings/chart_config/symbol_001")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["key"] == "symbol_001"

    @pytest.mark.asyncio
    async def test_get_setting_not_found(self, mock_user):
        """测试获取不存在的设置."""
        app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.api.v1.chart_settings import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        app.include_router(router, prefix="/api/v1")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/settings/chart_config/nonexistent")

        assert response.status_code == 200
        data = response.json()
        assert data["data"] is None


class TestSaveChartSetting:
    """测试保存设置."""

    @pytest.mark.asyncio
    async def test_save_new_setting(self, mock_user):
        """测试创建新设置."""
        app = FastAPI()
        mock_db = AsyncMock()

        # Mock查询返回None（不存在）
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        from app.api.v1.chart_settings import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        app.include_router(router, prefix="/api/v1")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/settings",
                params={"setting_type": "chart_config", "setting_key": "new_key"},
                json={"ma_periods": [5, 10]}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "设置已保存" in data["message"]

    @pytest.mark.asyncio
    async def test_save_update_existing_setting(self, mock_user, mock_setting):
        """测试更新现有设置."""
        app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_setting
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        from app.api.v1.chart_settings import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        app.include_router(router, prefix="/api/v1")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/settings",
                params={"setting_type": "chart_config", "setting_key": "symbol_001"},
                json={"ma_periods": [5, 10, 20, 60]}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "设置已更新" in data["message"]


class TestDeleteChartSetting:
    """测试删除设置."""

    @pytest.mark.asyncio
    async def test_delete_setting_success(self, mock_user, mock_setting):
        """测试成功删除设置."""
        app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_setting
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()

        from app.api.v1.chart_settings import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        app.include_router(router, prefix="/api/v1")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/settings/{mock_setting.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "设置已删除" in data["message"]

    @pytest.mark.asyncio
    async def test_delete_setting_not_found(self, mock_user):
        """测试删除不存在的设置."""
        app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.api.v1.chart_settings import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        app.include_router(router, prefix="/api/v1")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/settings/{uuid4()}")

        assert response.status_code == 404


class TestDeleteSettingsByType:
    """测试按类型删除设置."""

    @pytest.mark.asyncio
    async def test_delete_by_type_success(self, mock_user, mock_setting):
        """测试成功删除类型下所有设置."""
        app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalars().all.return_value = [mock_setting, mock_setting]
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()

        from app.api.v1.chart_settings import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        app.include_router(router, prefix="/api/v1")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete("/api/v1/settings/type/chart_config")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "已删除2个设置" in data["message"]

    @pytest.mark.asyncio
    async def test_delete_by_type_empty(self, mock_user):
        """测试删除空类型."""
        app = FastAPI()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalars().all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()

        from app.api.v1.chart_settings import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        app.include_router(router, prefix="/api/v1")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete("/api/v1/settings/type/nonexistent_type")

        assert response.status_code == 200
        data = response.json()
        assert "已删除0个设置" in data["message"]