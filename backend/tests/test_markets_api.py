"""
Markets API 测试.

测试市场类型管理API.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from app.main import app


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