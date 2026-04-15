"""
Auth API tests.

Tests for authentication API endpoints.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

from app.main import app


# =====================
# Login Tests
# =====================

class TestLoginAPI:
    """Login API endpoint tests."""

    @pytest.mark.asyncio
    async def test_login_user_not_found(self):
        """Test login with nonexistent user."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"username": "nonexistent_user_123", "password": "anypassword"},
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_invalid_password(self):
        """Test login with wrong password."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"username": "admin", "password": "wrongpassword"},
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_success_mocked(self):
        """Test successful login with mocked authentication."""
        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.username = "testuser"
        mock_user.role = "user"

        mock_session = MagicMock()
        mock_session.id = uuid4()

        mock_auth_service = AsyncMock(return_value=mock_user)
        mock_session_service = MagicMock()
        mock_session_service.create_session = AsyncMock(return_value=mock_session)

        with patch('app.api.v1.auth.authenticate_user', mock_auth_service):
            with patch('app.api.v1.auth.SessionService', return_value=mock_session_service):
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    response = await client.post(
                        "/api/v1/auth/login",
                        json={"username": "testuser", "password": "testpassword"},
                    )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_login_missing_fields(self):
        """Test login with missing required fields."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={},  # Missing username and password
            )

        # Should return validation error (422)
        assert response.status_code == 422


# =====================
# Logout Tests
# =====================

class TestLogoutAPI:
    """Logout API endpoint tests."""

    @pytest.mark.asyncio
    async def test_logout_success(self):
        """Test logout endpoint."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "登出成功" in data["message"]


# =====================
# Health Check Tests
# =====================

class TestHealthCheck:
    """Health check endpoint tests."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"