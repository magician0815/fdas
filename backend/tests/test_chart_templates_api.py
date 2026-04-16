"""
图表模板API测试.

测试chart_templates.py API路由.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import FastAPI, Depends
from httpx import AsyncClient, ASGITransport

from app.api.v1.chart_templates import router, TemplateCreateRequest, TemplateUpdateRequest, ApplyTemplateRequest
from app.services.chart_template_service import ChartTemplate, chart_template_service
from app.models.user import User


@pytest.fixture
def mock_user():
    """Mock用户."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.username = "testuser"
    return user


@pytest.fixture
def mock_template():
    """Mock模板."""
    return ChartTemplate(
        template_id="template_001",
        name="测试模板",
        description="测试描述",
        config={"ma_periods": [5, 10, 20]},
        is_public=False,
        creator_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_db():
    """Mock数据库会话."""
    return AsyncMock()


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


class TestCreateTemplate:
    """测试创建模板."""

    @pytest.mark.asyncio
    async def test_create_template_success(self, mock_user, mock_template, mock_db):
        """测试成功创建模板."""
        app = FastAPI()

        # 覆盖依赖
        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        # Mock服务
        with patch.object(chart_template_service, 'save_template', return_value=mock_template):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/templates",
                    json={
                        "name": "新模板",
                        "description": "描述",
                        "config": {"ma_periods": [5, 10]},
                        "is_public": False
                    }
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    @pytest.mark.asyncio
    async def test_create_template_minimal(self, mock_user, mock_template, mock_db):
        """测试最小化创建模板."""
        app = FastAPI()

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'save_template', return_value=mock_template):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/templates",
                    json={
                        "name": "简单模板",
                        "config": {}
                    }
                )

            assert response.status_code == 200


class TestListTemplates:
    """测试获取模板列表."""

    @pytest.mark.asyncio
    async def test_list_templates_user_only(self, mock_user, mock_template, mock_db):
        """测试获取用户模板."""
        app = FastAPI()

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'list_user_templates', return_value=[mock_template]), \
             patch.object(chart_template_service, 'list_public_templates', return_value=[]):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/templates")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_list_templates_include_public(self, mock_user, mock_template, mock_db):
        """测试获取包含公开模板的列表."""
        app = FastAPI()

        public_template = ChartTemplate(
            template_id="public_001",
            name="公开模板",
            description="",
            config={},
            is_public=True,
            creator_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'list_user_templates', return_value=[mock_template]), \
             patch.object(chart_template_service, 'list_public_templates', return_value=[public_template]):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/templates?include_public=true")

            assert response.status_code == 200
            data = response.json()
            assert len(data["data"]) == 2


class TestGetTemplate:
    """测试获取模板详情."""

    @pytest.mark.asyncio
    async def test_get_template_success(self, mock_user, mock_template, mock_db):
        """测试成功获取模板."""
        app = FastAPI()

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'load_template', return_value=mock_template):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/templates/template_001")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["name"] == "测试模板"

    @pytest.mark.asyncio
    async def test_get_template_not_found(self, mock_user, mock_db):
        """测试模板不存在."""
        app = FastAPI()

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'load_template', return_value=None):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/templates/nonexistent")

            assert response.status_code == 404


class TestUpdateTemplate:
    """测试更新模板."""

    @pytest.mark.asyncio
    async def test_update_template_success(self, mock_user, mock_template, mock_db):
        """测试成功更新模板."""
        app = FastAPI()

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'update_template', return_value=mock_template):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.put(
                    "/api/v1/templates/template_001",
                    json={
                        "name": "更新名称",
                        "description": "更新描述"
                    }
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    @pytest.mark.asyncio
    async def test_update_template_not_found(self, mock_user, mock_db):
        """测试更新不存在模板."""
        app = FastAPI()

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'update_template', return_value=None):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.put(
                    "/api/v1/templates/nonexistent",
                    json={"name": "新名称"}
                )

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_template_all_fields(self, mock_user, mock_template, mock_db):
        """测试更新所有字段."""
        app = FastAPI()

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'update_template', return_value=mock_template):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.put(
                    "/api/v1/templates/template_001",
                    json={
                        "name": "完整更新",
                        "description": "新描述",
                        "config": {"new_config": True},
                        "is_public": True
                    }
                )

            assert response.status_code == 200


class TestDeleteTemplate:
    """测试删除模板."""

    @pytest.mark.asyncio
    async def test_delete_template_success(self, mock_user, mock_db):
        """测试成功删除模板."""
        app = FastAPI()

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'delete_template', return_value=True):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.delete("/api/v1/templates/template_001")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_template_not_found(self, mock_user, mock_db):
        """测试删除不存在模板."""
        app = FastAPI()

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'delete_template', return_value=False):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.delete("/api/v1/templates/nonexistent")

            assert response.status_code == 404


class TestApplyTemplate:
    """测试应用模板."""

    @pytest.mark.asyncio
    async def test_apply_template_success(self, mock_user, mock_template, mock_db):
        """测试成功应用模板."""
        app = FastAPI()

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'load_template', return_value=mock_template), \
             patch.object(chart_template_service, 'apply_template_to_chart', return_value=True):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/templates/template_001/apply",
                    json={"symbol_id": str(uuid4())}
                )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_apply_template_not_found(self, mock_user, mock_db):
        """测试应用不存在模板."""
        app = FastAPI()

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'load_template', return_value=None):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/templates/nonexistent/apply",
                    json={"symbol_id": str(uuid4())}
                )

            assert response.status_code == 404


class TestGetShareLink:
    """测试获取分享链接."""

    @pytest.mark.asyncio
    async def test_get_share_link_success(self, mock_user, mock_template, mock_db):
        """测试成功获取分享链接."""
        app = FastAPI()

        # 设置模板创建者为当前用户
        mock_template.creator_id = mock_user.id

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'load_template', return_value=mock_template), \
             patch.object(chart_template_service, 'generate_share_link', return_value="http://share.link/template_001"):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/templates/template_001/share")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "share_link" in data["data"]

    @pytest.mark.asyncio
    async def test_get_share_link_not_found(self, mock_user, mock_db):
        """测试模板不存在."""
        app = FastAPI()

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'load_template', return_value=None):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/templates/nonexistent/share")

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_share_link_public_template(self, mock_user, mock_template, mock_db):
        """测试公开模板的分享链接."""
        app = FastAPI()

        mock_template.is_public = True
        mock_template.creator_id = uuid4()  # 其他用户创建

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'load_template', return_value=mock_template), \
             patch.object(chart_template_service, 'generate_share_link', return_value="http://share.link/template_001"):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/templates/template_001/share")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_share_link_forbidden(self, mock_user, mock_template, mock_db):
        """测试无权限分享模板（covers line 228）."""
        app = FastAPI()

        # 设置模板创建者为其他用户，且非公开
        mock_template.is_public = False
        mock_template.creator_id = uuid4()  # 其他用户创建

        from app.api.v1.chart_templates import require_login, get_db
        app.dependency_overrides[require_login] = override_require_login(mock_user)
        app.dependency_overrides[get_db] = override_get_db(mock_db)

        with patch.object(chart_template_service, 'load_template', return_value=mock_template):
            app.include_router(router, prefix="/api/v1")

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/v1/templates/template_001/share")

            assert response.status_code == 403