"""
FX Data API tests.

Tests for forex daily data API endpoints - focusing on unauthorized cases.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from app.main import app


# =====================
# Unauthorized Tests - These don't require complex mocking
# =====================

class TestFXDataAPIUnauthorized:
    """Test unauthorized access to FX data API."""

    @pytest.mark.asyncio
    async def test_get_fx_data_unauthorized(self):
        """Test get FX data without authentication."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/fx/data")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_fx_data_by_id_unauthorized(self):
        """Test get FX data by ID without authentication."""
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
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/fx/indicators")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_fx_data_no_session_header(self):
        """Test get FX data without session header."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/fx/data",
                params={"symbol_code": "USDCNY"}
            )

        assert response.status_code == 401


# =====================
# Parameter Validation Tests (when unauthorized)
# =====================

class TestFXDataAPIParams:
    """Test parameter validation."""

    @pytest.mark.asyncio
    async def test_get_fx_data_invalid_uuid(self):
        """Test get FX data by ID with invalid UUID format."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/fx/data/not-a-uuid")

        # Should return 401 (auth check happens first) or 422 (validation)
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_get_fx_data_with_params_unauthorized(self):
        """Test get FX data with parameters but unauthorized."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/fx/data",
                params={
                    "symbol_code": "USDCNY",
                    "period": "weekly",
                    "limit": 100,
                }
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_indicators_with_params_unauthorized(self):
        """Test get indicators with parameters but unauthorized."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/fx/indicators",
                params={
                    "symbol_code": "USDCNY",
                    "period": "monthly",
                }
            )

        assert response.status_code == 401


# =====================
# Response Format Tests
# =====================

class TestFXDataAPIResponseFormat:
    """Test response format."""

    @pytest.mark.asyncio
    async def test_unauthorized_response_format(self):
        """Test unauthorized response format."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/fx/data")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data