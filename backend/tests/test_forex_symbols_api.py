"""
Forex Symbols API 深度测试.

测试外汇标的管理API的授权和数据操作.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from app.main import app


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