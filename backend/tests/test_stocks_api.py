"""
Stocks API 测试.

测试股票数据API（这些API不需要认证）.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


class TestStocksAPIPublic:
    """测试公开访问的API."""

    @pytest.mark.asyncio
    async def test_get_market_type_public(self):
        """测试市场识别（公开API）."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/stocks/market-type",
                params={"symbol_code": "600000"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["symbol_code"] == "600000"
        assert data["market_type"] == "stock_a"

    @pytest.mark.asyncio
    async def test_get_market_type_forex(self):
        """测试外汇市场识别."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/stocks/market-type",
                params={"symbol_code": "EURUSD"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["market_type"] == "forex"

    @pytest.mark.asyncio
    async def test_get_market_type_kcb(self):
        """测试科创板识别."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/stocks/market-type",
                params={"symbol_code": "688001"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["market_type"] == "stock_kcb"

    @pytest.mark.asyncio
    async def test_get_market_type_cyb(self):
        """测试创业板识别."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/stocks/market-type",
                params={"symbol_code": "300001"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["market_type"] == "stock_cyb"

    @pytest.mark.asyncio
    async def test_get_adjustment_data(self):
        """测试复权数据."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/stocks/adjustment",
                params={
                    "symbol_id": "test123",
                    "adjustment_type": "forward"
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["symbol_id"] == "test123"
        assert data["adjustment_type"] == "forward"
        assert "data" in data

    @pytest.mark.asyncio
    async def test_get_dividend_events(self):
        """测试除权除息事件."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/stocks/dividend-events",
                params={"symbol_id": "test123"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["symbol_id"] == "test123"
        assert "events" in data


class TestStocksAPIResponseFormat:
    """测试响应格式."""

    @pytest.mark.asyncio
    async def test_market_type_response_format(self):
        """测试市场识别响应格式."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/stocks/market-type",
                params={"symbol_code": "600000"}
            )

        assert response.status_code == 200
        data = response.json()
        assert "symbol_code" in data
        assert "market_type" in data
        assert "config" in data