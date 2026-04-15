"""
Datasources API tests.

Tests for datasource management API endpoints.

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

class TestDatasourcesAPIUnauthorized:
    """Test unauthorized access to datasources API."""

    @pytest.mark.asyncio
    async def test_list_datasources_unauthorized(self):
        """Test list datasources without authentication."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/datasources/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_datasource_unauthorized(self):
        """Test get datasource without authentication."""
        datasource_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/datasources/{datasource_id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_datasource_unauthorized(self):
        """Test create datasource without authentication."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/datasources/", json={})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_datasource_unauthorized(self):
        """Test update datasource without authentication."""
        datasource_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(f"/api/v1/datasources/{datasource_id}", json={})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_datasource_unauthorized(self):
        """Test delete datasource without authentication."""
        datasource_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.delete(f"/api/v1/datasources/{datasource_id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_supported_symbols_unauthorized(self):
        """Test get supported symbols without authentication."""
        datasource_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/datasources/{datasource_id}/symbols")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_fetch_compare_symbols_unauthorized(self):
        """Test fetch and compare symbols without authentication."""
        datasource_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(f"/api/v1/datasources/{datasource_id}/symbols/fetch")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_supported_symbols_unauthorized(self):
        """Test update supported symbols without authentication."""
        datasource_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(f"/api/v1/datasources/{datasource_id}/symbols")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_sync_symbols_to_database_unauthorized(self):
        """Test sync symbols to database without authentication."""
        datasource_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(f"/api/v1/datasources/{datasource_id}/sync-to-database")

        assert response.status_code == 401


# =====================
# Parameter Validation Tests
# =====================

class TestDatasourcesAPIParams:
    """Test parameter validation."""

    @pytest.mark.asyncio
    async def test_get_datasource_invalid_uuid(self):
        """Test get datasource with invalid UUID."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/datasources/not-a-uuid")

        # Should return 401 (auth check first) or 422 (validation)
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_delete_datasource_invalid_uuid(self):
        """Test delete datasource with invalid UUID."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.delete("/api/v1/datasources/not-a-uuid")

        assert response.status_code in [401, 422]


# =====================
# Response Format Tests
# =====================

class TestDatasourcesAPIResponseFormat:
    """Test response format."""

    @pytest.mark.asyncio
    async def test_unauthorized_response_format(self):
        """Test unauthorized response format."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/datasources/")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data