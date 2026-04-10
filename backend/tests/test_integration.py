"""
集成测试.

测试端到端流程: 用户注册 -> 登录 -> 数据采集 -> 指标计算 -> 登出.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-10 - 适配新的ForexDaily模型和forex_daily_service
"""

from __future__ import annotations

import pytest
import uuid
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.models.user import User
from app.models.forex_daily import ForexDaily
from app.models.forex_symbol import ForexSymbol
from app.models.datasource import DataSource
from app.models.market import Market
from app.models.session import Session
from app.services.auth_service import hash_password
from app.services.forex_daily_service import forex_daily_service
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
async def test_market(db_session):
    """创建测试市场类型."""
    market = Market(
        code=f"test_forex_{uuid.uuid4().hex[:4]}",
        name="测试外汇市场",
        timezone="Asia/Shanghai",
        is_active=True,
    )
    db_session.add(market)
    await db_session.commit()
    await db_session.refresh(market)
    return market


@pytest.fixture
async def test_datasource(db_session, test_market):
    """创建测试数据源."""
    datasource = DataSource(
        name=f"测试数据源_{uuid.uuid4().hex[:4]}",
        market_id=test_market.id,
        interface="forex_hist",
        description="测试用数据源",
        config_schema={"symbol": {"type": "string"}, "start_date": {"type": "date"}},
        is_active=True,
    )
    db_session.add(datasource)
    await db_session.commit()
    await db_session.refresh(datasource)
    return datasource


@pytest.fixture
async def test_forex_symbol(db_session, test_datasource):
    """创建测试外汇标的."""
    unique_code = f"USDCNH_TEST_{uuid.uuid4().hex[:4]}"
    symbol = ForexSymbol(
        code=unique_code,
        name=f"测试美元人民币_{uuid.uuid4().hex[:4]}",
        datasource_id=test_datasource.id,
        base_currency="USD",
        quote_currency="CNY",
        is_active=True,
    )
    db_session.add(symbol)
    await db_session.commit()
    await db_session.refresh(symbol)
    return symbol


@pytest.fixture
async def test_forex_daily_data(db_session, test_forex_symbol, test_datasource):
    """创建测试外汇日线数据."""
    data = [
        ForexDaily(
            symbol_id=test_forex_symbol.id,
            datasource_id=test_datasource.id,
            date=date(2026, 5, 1),
            open=7.10, high=7.15, low=7.08, close=7.12,
            change_pct=0.28, change_amount=0.02, amplitude=0.99,
        ),
        ForexDaily(
            symbol_id=test_forex_symbol.id,
            datasource_id=test_datasource.id,
            date=date(2026, 5, 2),
            open=7.12, high=7.18, low=7.10, close=7.16,
            change_pct=0.56, change_amount=0.04, amplitude=1.12,
        ),
        ForexDaily(
            symbol_id=test_forex_symbol.id,
            datasource_id=test_datasource.id,
            date=date(2026, 5, 3),
            open=7.16, high=7.20, low=7.14, close=7.18,
            change_pct=0.28, change_amount=0.02, amplitude=0.84,
        ),
        ForexDaily(
            symbol_id=test_forex_symbol.id,
            datasource_id=test_datasource.id,
            date=date(2026, 5, 4),
            open=7.18, high=7.22, low=7.16, close=7.20,
            change_pct=0.28, change_amount=0.02, amplitude=0.84,
        ),
        ForexDaily(
            symbol_id=test_forex_symbol.id,
            datasource_id=test_datasource.id,
            date=date(2026, 5, 5),
            open=7.20, high=7.25, low=7.18, close=7.22,
            change_pct=0.28, change_amount=0.02, amplitude=0.97,
        ),
    ]
    for item in data:
        db_session.add(item)
    await db_session.commit()
    return data, test_forex_symbol


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
    async def test_fx_data_flow(self, client, test_user, test_forex_daily_data):
        """测试汇率数据查询流程."""
        fx_data, test_symbol = test_forex_daily_data

        # 1. 登录获取session_id
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "testpassword"}
        )
        assert login_resp.status_code == 200
        session_id = login_resp.json()["data"]["session_id"]

        # 2. 查询汇率数据（使用symbol_code参数）
        data_resp = await client.get(
            "/api/v1/fx/data",
            params={"symbol_code": test_symbol.code, "start_date": "2026-05-01", "end_date": "2026-05-05"}
        )
        assert data_resp.status_code == 200
        data = data_resp.json()["data"]
        assert len(data) == 5

        # 3. 查询技术指标
        indicators_resp = await client.get(
            "/api/v1/fx/indicators",
            params={"symbol_code": test_symbol.code, "ma_period": 3}
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
    async def test_ma_calculation_with_real_data(self, db_session, test_forex_symbol, test_datasource):
        """测试MA计算与真实数据."""
        prices = [7.12, 7.16, 7.18, 7.20, 7.22]
        data_list = []
        for i, price in enumerate(prices):
            data = ForexDaily(
                symbol_id=test_forex_symbol.id,
                datasource_id=test_datasource.id,
                date=date(2026, 6, i+1),
                close=price,
                open=price - 0.02,
                high=price + 0.03,
                low=price - 0.04,
                change_pct=0.28,
                change_amount=0.02,
                amplitude=1.0,
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
    async def test_data_save_and_query(self, db_session, test_forex_symbol, test_datasource):
        """测试数据保存和查询."""
        # 准备测试数据（符合新的ForexDaily结构）
        test_data = [
            {
                "symbol_id": test_forex_symbol.id,
                "datasource_id": test_datasource.id,
                "date": date(2026, 4, 1),
                "open": 7.25,
                "high": 7.30,
                "low": 7.22,
                "close": 7.28,
                "change_pct": 0.42,
                "change_amount": 0.03,
                "amplitude": 1.11,
            }
        ]
        await forex_daily_service.save_forex_daily(db_session, test_data)

        # 查询验证
        result = await db_session.execute(
            select(ForexDaily).where(
                ForexDaily.symbol_id == test_forex_symbol.id,
                ForexDaily.date == date(2026, 4, 1)
            )
        )
        saved_data = result.scalar_one()
        assert float(saved_data.close) == 7.28
        assert float(saved_data.change_pct) == 0.42

    @pytest.mark.asyncio
    async def test_get_latest_date(self, db_session, test_forex_symbol, test_datasource):
        """测试获取最新数据日期."""
        # 创建测试数据
        test_data = [
            {
                "symbol_id": test_forex_symbol.id,
                "datasource_id": test_datasource.id,
                "date": date(2026, 3, 15),
                "open": 7.20,
                "high": 7.25,
                "low": 7.18,
                "close": 7.22,
            },
            {
                "symbol_id": test_forex_symbol.id,
                "datasource_id": test_datasource.id,
                "date": date(2026, 3, 20),
                "open": 7.22,
                "high": 7.28,
                "low": 7.20,
                "close": 7.25,
            },
        ]
        await forex_daily_service.save_forex_daily(db_session, test_data)

        # 获取最新日期
        latest_date = await forex_daily_service.get_latest_date(db_session, test_forex_symbol.id)
        assert latest_date == date(2026, 3, 20)