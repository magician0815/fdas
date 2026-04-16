"""
Main app tests.

Tests for FastAPI application lifespan and health check.

Author: FDAS Team
Created: 2026-04-15
Updated: 2026-04-15 - 改为测试lifespan handler
Updated: 2026-04-16 - 添加SESSION_SECRET环境变量mock
"""

import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient, ASGITransport

from app.main import app


class TestLifespan:
    """测试应用生命周期管理."""

    @pytest.mark.asyncio
    async def test_lifespan_startup(self):
        """测试lifespan启动逻辑."""
        # 设置SESSION_SECRET环境变量
        with patch.dict(os.environ, {'SESSION_SECRET': 'test-secret-key'}):
            with patch('app.services.scheduler_service.scheduler_service') as mock_scheduler:
                with patch('app.services.collection_service.collection_service') as mock_collection:
                    mock_scheduler.start = MagicMock()
                    mock_collection.load_enabled_tasks = AsyncMock()

                    # 重新导入settings以加载环境变量
                    from app.config.settings import Settings
                    test_settings = Settings()

                    with patch('app.main.settings', test_settings):
                        # 导入lifespan并测试启动部分
                        from app.main import lifespan

                        # 创建mock app
                        mock_app = MagicMock()

                        # 测试启动阶段
                        async with lifespan(mock_app):
                            mock_scheduler.start.assert_called_once()
                            mock_collection.load_enabled_tasks.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_shutdown(self):
        """测试lifespan关闭逻辑."""
        # 设置SESSION_SECRET环境变量
        with patch.dict(os.environ, {'SESSION_SECRET': 'test-secret-key'}):
            with patch('app.services.scheduler_service.scheduler_service') as mock_scheduler:
                with patch('app.services.collection_service.collection_service') as mock_collection:
                    mock_scheduler.start = MagicMock()
                    mock_scheduler.shutdown = MagicMock()
                    mock_collection.load_enabled_tasks = AsyncMock()

                    from app.config.settings import Settings
                    test_settings = Settings()

                    with patch('app.main.settings', test_settings):
                        from app.main import lifespan
                        mock_app = MagicMock()

                        # 进入lifespan后退出，触发shutdown
                        async with lifespan(mock_app):
                            # 启动已验证
                            pass

                        # 验证shutdown被调用
                        mock_scheduler.shutdown.assert_called_once_with(wait=True)


class TestHealthCheck:
    """测试健康检查接口."""

    @pytest.mark.asyncio
    async def test_health_check_endpoint(self):
        """测试健康检查接口."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.1"