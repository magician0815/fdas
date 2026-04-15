"""
Users API tests.

Tests for user management API endpoints - focusing on unauthorized cases.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from app.main import app


# =====================
# Unauthorized Tests - These don't require mocking
# =====================

class TestUsersAPIUnauthorized:
    """Test unauthorized access to users API."""

    @pytest.mark.asyncio
    async def test_list_users_unauthorized(self):
        """Test list users without authentication."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/users/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_user_unauthorized(self):
        """Test create user without authentication."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/users/", json={})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_user_unauthorized(self):
        """Test update user without authentication."""
        user_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(f"/api/v1/users/{user_id}", json={})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_user_unauthorized(self):
        """Test delete user without authentication."""
        user_id = str(uuid4())
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.delete(f"/api/v1/users/{user_id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_users_no_session_header(self):
        """Test list users without session header."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/users/")

        # Should return 401 (no session)
        assert response.status_code == 401


# =====================
# Response Format Tests
# =====================

class TestUsersAPIResponseFormat:
    """Test response format when unauthorized."""

    @pytest.mark.asyncio
    async def test_unauthorized_response_format(self):
        """Test unauthorized response format."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/users/")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data