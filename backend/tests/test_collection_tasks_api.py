"""
Collection Tasks API tests.

Tests for collection task management API endpoints.

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

class TestCollectionTasksAPIUnauthorized:
    """Test unauthorized access to collection tasks API."""

    @pytest.mark.asyncio
    async def test_list_collection_tasks_unauthorized(self):
        """Test list collection tasks without authentication."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/collection-tasks/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_collection_task_unauthorized(self):
        """Test get collection task without authentication."""
        task_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/collection-tasks/{task_id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_collection_task_unauthorized(self):
        """Test create collection task without authentication."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/collection-tasks/", json={})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_collection_task_unauthorized(self):
        """Test update collection task without authentication."""
        task_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(f"/api/v1/collection-tasks/{task_id}", json={})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_collection_task_unauthorized(self):
        """Test delete collection task without authentication."""
        task_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.delete(f"/api/v1/collection-tasks/{task_id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_enable_collection_task_unauthorized(self):
        """Test enable collection task without authentication."""
        task_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(f"/api/v1/collection-tasks/{task_id}/enable")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_disable_collection_task_unauthorized(self):
        """Test disable collection task without authentication."""
        task_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(f"/api/v1/collection-tasks/{task_id}/disable")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_execute_collection_task_unauthorized(self):
        """Test execute collection task without authentication."""
        task_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(f"/api/v1/collection-tasks/{task_id}/execute")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_task_logs_unauthorized(self):
        """Test get task logs without authentication."""
        task_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/collection-tasks/{task_id}/logs")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_validate_params_unauthorized(self):
        """Test validate collection params without authentication."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/collection-tasks/validate", json={})

        assert response.status_code == 401


# =====================
# Parameter Validation Tests
# =====================

class TestCollectionTasksAPIParams:
    """Test parameter validation."""

    @pytest.mark.asyncio
    async def test_get_collection_task_invalid_uuid(self):
        """Test get collection task with invalid UUID."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/collection-tasks/not-a-uuid")

        # Should return 401 (auth check first) or 422 (validation)
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_list_collection_tasks_with_market_filter_unauthorized(self):
        """Test list tasks with market filter but unauthorized."""
        market_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/collection-tasks/",
                params={"market_id": market_id}
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_task_logs_with_limit_unauthorized(self):
        """Test get task logs with limit but unauthorized."""
        task_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/collection-tasks/{task_id}/logs",
                params={"limit": 10}
            )

        assert response.status_code == 401