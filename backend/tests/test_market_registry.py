"""
市场服务注册表测试.

测试目标:
- register: 注册新市场
- get_info: 获取市场信息
- is_supported: 检查市场支持
- get_symbol_model: 获取标的模型
- get_daily_model: 获取日线模型
- get_service_name: 获取服务名称
- get_all_markets: 获取所有市场
- get_stock_markets: 获取股票市场列表
- get_bond_markets: 获取债券市场列表
- get_market_code_by_id: 根据ID获取市场代码

Author: FDAS Team
Created: 2026-04-29
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.market_registry import MarketRegistry, MarketInfo
from app.models.forex_symbol import ForexSymbol
from app.models.forex_daily import ForexDaily
from app.models.stock_symbol import StockSymbol
from app.models.stock_daily import StockDaily
from app.models.bond_symbol import BondSymbol
from app.models.bond_daily import BondDaily
from app.models.futures_variety import FuturesVariety
from app.models.futures_daily import FuturesDaily


class TestMarketRegistry:
    """市场注册表基础测试."""

    def test_get_info_valid_market(self):
        info = MarketRegistry.get_info("forex")
        assert info is not None
        assert info.market_code == "forex"
        assert info.name == "外汇"
        assert info.symbol_model == ForexSymbol
        assert info.daily_model == ForexDaily
        assert info.service_name == "forex_daily_service"
        assert info.supports_multiple is False

    def test_get_info_all_stock_markets(self):
        for code in ["stock_cn", "stock_us", "stock_hk"]:
            info = MarketRegistry.get_info(code)
            assert info is not None, f"{code} should be registered"
            assert info.symbol_model == StockSymbol
            assert info.daily_model == StockDaily
            assert info.service_name == "stock_daily_service"

    def test_get_info_all_bond_markets(self):
        for code in ["bond_cn", "bond_us"]:
            info = MarketRegistry.get_info(code)
            assert info is not None, f"{code} should be registered"
            assert info.symbol_model == BondSymbol
            assert info.daily_model == BondDaily
            assert info.service_name == "bond_daily_service"

    def test_get_info_futures(self):
        info = MarketRegistry.get_info("futures_cn")
        assert info is not None
        assert info.symbol_model == FuturesVariety
        assert info.daily_model == FuturesDaily
        assert info.service_name == "futures_daily_service"

    def test_get_info_unknown_market(self):
        assert MarketRegistry.get_info("unknown") is None
        assert MarketRegistry.get_info("") is None

    def test_is_supported_valid(self):
        assert MarketRegistry.is_supported("forex") is True
        assert MarketRegistry.is_supported("stock_cn") is True
        assert MarketRegistry.is_supported("bond_us") is True

    def test_is_supported_invalid(self):
        assert MarketRegistry.is_supported("unknown") is False
        assert MarketRegistry.is_supported("") is False

    def test_get_symbol_model(self):
        assert MarketRegistry.get_symbol_model("forex") == ForexSymbol
        assert MarketRegistry.get_symbol_model("stock_cn") == StockSymbol
        assert MarketRegistry.get_symbol_model("unknown") is None

    def test_get_daily_model(self):
        assert MarketRegistry.get_daily_model("forex") == ForexDaily
        assert MarketRegistry.get_daily_model("futures_cn") == FuturesDaily
        assert MarketRegistry.get_daily_model("unknown") is None

    def test_get_service_name(self):
        assert MarketRegistry.get_service_name("forex") == "forex_daily_service"
        assert MarketRegistry.get_service_name("stock_cn") == "stock_daily_service"
        assert MarketRegistry.get_service_name("bond_cn") == "bond_daily_service"
        assert MarketRegistry.get_service_name("unknown") is None

    def test_get_all_markets_returns_copy(self):
        all_markets = MarketRegistry.get_all_markets()
        assert len(all_markets) == 7
        assert "forex" in all_markets
        assert "stock_cn" in all_markets
        assert "futures_cn" in all_markets
        # mutation safety
        all_markets["test"] = None
        assert "test" not in MarketRegistry.get_all_markets()

    def test_get_stock_markets(self):
        stock_markets = MarketRegistry.get_stock_markets()
        assert len(stock_markets) == 3
        assert "stock_cn" in stock_markets
        assert "stock_us" in stock_markets
        assert "stock_hk" in stock_markets

    def test_get_bond_markets(self):
        bond_markets = MarketRegistry.get_bond_markets()
        assert len(bond_markets) == 2
        assert "bond_cn" in bond_markets
        assert "bond_us" in bond_markets


class TestRegisterNewMarket:
    """注册新市场测试."""

    def test_register_new_market(self):
        new_market = MarketInfo(
            market_code="crypto",
            name="加密货币",
            symbol_model=ForexSymbol,
            daily_model=ForexDaily,
            service_name="crypto_service",
            supports_multiple=True,
        )
        MarketRegistry.register(new_market)
        assert MarketRegistry.is_supported("crypto") is True
        info = MarketRegistry.get_info("crypto")
        assert info.name == "加密货币"
        assert info.supports_multiple is True

    def test_register_overwrites_existing(self):
        updated = MarketInfo(
            market_code="forex",
            name="外汇市场(更新)",
            symbol_model=ForexSymbol,
            daily_model=ForexDaily,
            service_name="forex_daily_service",
            supports_multiple=True,
        )
        MarketRegistry.register(updated)
        info = MarketRegistry.get_info("forex")
        assert info.name == "外汇市场(更新)"
        assert info.supports_multiple is True


class TestGetMarketCodeById:
    """异步DB查询market_code测试."""

    @pytest.mark.asyncio
    async def test_get_market_code_by_id_found(self):
        mock_db = AsyncMock()
        market_id = uuid4()
        mock_market = MagicMock()
        mock_market.code = "forex"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_market
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await MarketRegistry.get_market_code_by_id(market_id, mock_db)
        assert result == "forex"
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_market_code_by_id_not_found(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await MarketRegistry.get_market_code_by_id(uuid4(), mock_db)
        assert result is None
