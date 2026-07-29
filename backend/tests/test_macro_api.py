"""宏观看板 API 测试."""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


class TestMacroConfigsAPI:
    """配置 API — 数据库相关测试需单独运行 (ASGITransport 并发冲突)."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需服务器单独运行: ASGITransport 与 APScheduler 连接池冲突")
    async def test_list_configs(self):
        """配置列表应返回5个种子数据源."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/macro/configs")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total"] == 5

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需服务器单独运行: ASGITransport 与 APScheduler 连接池冲突")
    async def test_get_config_not_found(self):
        """获取不存在的配置返回 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/macro/configs/{fake_id}")
        assert response.status_code == 404


class TestMacroDataAPI:
    """数据 API."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需服务器单独运行: ASGITransport 与 APScheduler 连接池冲突")
    async def test_get_latest_not_found(self):
        """获取不存在源的最新数据返回 404."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/macro/data/unknown-source/latest")
        assert response.status_code == 404


class TestHealthCheck:
    """健康检查 — 不依赖数据库."""

    @pytest.mark.asyncio
    async def test_version(self):
        """验证版本号为 2.0.0."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["version"] == "2.0.0"
