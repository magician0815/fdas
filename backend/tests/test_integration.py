"""
集成测试.

测试端到端流程: 用户注册 -> 登录 -> 数据采集 -> 指标计算 -> 登出.
"""

from __future__ import annotations

import pytest
import uuid
from datetime import date
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.models.user import User
from app.models.fx_data import FXData
from app.models.session import Session
from app.services.auth_service import hash_password
from app.services.fx_data_service import fx_data_service
from app.services.technical_service import technical_service


@pytest.fixture
async def client():
    """创建测试客户端."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def test_user(db_session):
    """创建测试用户."""
    username = f"integration_user_{uuid.uuid4().hex[:8]}"
    user = User(
        username=username,
        password_hash=hash_password("testpassword"),
        role="user"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session):
    """创建管理员用户."""
    username = f"integration_admin_{uuid.uuid4().hex[:8]}"
    user = User(
        username=username,
        password_hash=hash_password("adminpassword"),
        role="admin"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_fx_data(db_session):
    """创建测试汇率数据."""
    # 使用唯一符号避免与数据库现有数据冲突
    unique_symbol = f"USDCNH_TEST_{uuid.uuid4().hex[:4]}"
    data = [
        FXData(symbol=unique_symbol, date=date(2026, 5, 1), open=7.10, high=7.15, low=7.08, close=7.12, volume=1000),
        FXData(symbol=unique_symbol, date=date(2026, 5, 2), open=7.12, high=7.18, low=7.10, close=7.16, volume=1100),
        FXData(symbol=unique_symbol, date=date(2026, 5, 3), open=7.16, high=7.20, low=7.14, close=7.18, volume=1200),
        FXData(symbol=unique_symbol, date=date(2026, 5, 4), open=7.18, high=7.22, low=7.16, close=7.20, volume=1300),
        FXData(symbol=unique_symbol, date=date(2026, 5, 5), open=7.20, high=7.25, low=7.18, close=7.22, volume=1400),
    ]
    for item in data:
        db_session.add(item)
    await db_session.commit()
    return data, unique_symbol


class TestIntegration:
    """集成测试套件."""

    @pytest.mark.asyncio
    async def test_user_login_logout_flow(self, client, test_user):
        """测试用户登录登出流程."""
        # 1. 登录
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "testpassword"}
        )
        assert login_resp.status_code == 200
        assert login_resp.json()["success"] is True
        # session_id在响应body中返回
        assert "session_id" in login_resp.json()["data"]

        # 2. 登出
        logout_resp = await client.post("/api/v1/auth/logout")
        assert logout_resp.status_code == 200
        assert logout_resp.json()["success"] is True

    @pytest.mark.asyncio
    async def test_fx_data_flow(self, client, test_user, test_fx_data):
        """测试汇率数据查询流程."""
        fx_data, unique_symbol = test_fx_data

        # 1. 登录获取session_id
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "testpassword"}
        )
        assert login_resp.status_code == 200
        session_id = login_resp.json()["data"]["session_id"]

        # 2. 查询汇率数据（当前实现不需要认证）
        data_resp = await client.get(
            "/api/v1/fx/data",
            params={"symbol": unique_symbol, "start_date": "2026-05-01", "end_date": "2026-05-05"}
        )
        assert data_resp.status_code == 200
        data = data_resp.json()["data"]
        assert len(data) == 5

        # 3. 查询技术指标
        indicators_resp = await client.get(
            "/api/v1/fx/indicators",
            params={"symbol": unique_symbol, "ma_period": 3}
        )
        assert indicators_resp.status_code == 200
        indicators = indicators_resp.json()["data"]
        assert "ma" in indicators

    @pytest.mark.asyncio
    async def test_invalid_login(self, client, test_user):
        """测试无效登录."""
        # 1. 错误密码
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "wrongpassword"}
        )
        assert resp.status_code == 401

        # 2. 不存在的用户
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "password"}
        )
        assert resp.status_code == 401


class TestTechnicalIndicatorsIntegration:
    """技术指标集成测试."""

    @pytest.mark.asyncio
    async def test_ma_calculation_with_real_data(self, db_session):
        """测试MA计算与真实数据."""
        # 使用唯一符号避免冲突
        unique_symbol = f"USDCNH_MA_{uuid.uuid4().hex[:4]}"
        prices = [7.12, 7.16, 7.18, 7.20, 7.22]
        data_list = []
        for i, price in enumerate(prices):
            data = FXData(
                symbol=unique_symbol,
                date=date(2026, 6, i+1),
                close=price,
                open=price - 0.02,
                high=price + 0.03,
                low=price - 0.04,
                volume=1000 + i * 100
            )
            db_session.add(data)
            data_list.append(data)
        await db_session.commit()

        # 计算MA（使用服务接口）
        ma_result = technical_service.calculate_ma(data_list, period=3)

        # 验证MA结果
        assert len(ma_result) == 3
        assert abs(ma_result[0]["value"] - 7.1533) < 0.01
        assert abs(ma_result[1]["value"] - 7.18) < 0.01
        assert abs(ma_result[2]["value"] - 7.20) < 0.01


class TestDataCollectionIntegration:
    """数据采集集成测试."""

    @pytest.mark.asyncio
    async def test_data_save_and_query(self, db_session):
        """测试数据保存和查询."""
        # 使用唯一日期避免冲突
        test_data = [
            {
                "symbol": "USDCNH_TEST2",
                "date": date(2026, 4, 1),
                "open": 7.25,
                "high": 7.30,
                "low": 7.22,
                "close": 7.28,
                "volume": 2000
            }
        ]
        await fx_data_service.save_fx_data(db_session, test_data)

        # 查询验证
        result = await db_session.execute(
            select(FXData).where(FXData.symbol == "USDCNH_TEST2", FXData.date == date(2026, 4, 1))
        )
        saved_data = result.scalar_one()
        assert float(saved_data.close) == 7.28
        assert saved_data.volume == 2000