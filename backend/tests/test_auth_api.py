"""
登录API测试.

Author: FDAS Team
Created: 2026-04-03
"""

import pytest
import uuid
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_login_user_not_found():
    """测试用户不存在."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": f"nonexistent_{uuid.uuid4().hex}", "password": "anypassword"},
        )

    # 用户不存在应返回401
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_logout_success():
    """测试登出成功."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "登出成功" in data["message"]


# ============ 用户CRUD API测试 ============

@pytest.mark.asyncio
async def test_list_users_unauthorized():
    """测试未授权访问用户列表."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/users/")

    # 未授权应返回401
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_user_unauthorized():
    """测试创建用户未授权."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # 未登录访问
        response = await client.post("/api/v1/users/", json={})

    # 未授权应返回401
    assert response.status_code == 401