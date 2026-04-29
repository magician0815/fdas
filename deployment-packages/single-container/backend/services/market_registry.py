"""
市场服务注册表。

提供市场代码到服务/模型的映射，支持多市场统一分派。

Author: FDAS Team
Created: 2026-04-23
"""

from typing import Optional, Dict, Type, Any
from uuid import UUID
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.forex_symbol import ForexSymbol
from app.models.forex_daily import ForexDaily
from app.models.stock_symbol import StockSymbol
from app.models.stock_daily import StockDaily
from app.models.bond_symbol import BondSymbol
from app.models.bond_daily import BondDaily
from app.models.futures_variety import FuturesVariety
from app.models.futures_contract import FuturesContract
from app.models.futures_daily import FuturesDaily
from app.models.market import Market


@dataclass
class MarketInfo:
    """市场信息数据结构."""
    market_code: str
    name: str
    symbol_model: Type
    daily_model: Type
    service_name: str
    supports_multiple: bool


class MarketRegistry:
    """
    市场服务注册表。

    管理所有市场代码到服务/模型的映射，支持多市场统一分派。
    """

    _registry: Dict[str, MarketInfo] = {
        "forex": MarketInfo(
            market_code="forex",
            name="外汇",
            symbol_model=ForexSymbol,
            daily_model=ForexDaily,
            service_name="forex_daily_service",
            supports_multiple=False,
        ),
        "stock_cn": MarketInfo(
            market_code="stock_cn",
            name="A股",
            symbol_model=StockSymbol,
            daily_model=StockDaily,
            service_name="stock_daily_service",
            supports_multiple=True,
        ),
        "stock_us": MarketInfo(
            market_code="stock_us",
            name="美股",
            symbol_model=StockSymbol,
            daily_model=StockDaily,
            service_name="stock_daily_service",
            supports_multiple=True,
        ),
        "stock_hk": MarketInfo(
            market_code="stock_hk",
            name="港股",
            symbol_model=StockSymbol,
            daily_model=StockDaily,
            service_name="stock_daily_service",
            supports_multiple=True,
        ),
        "futures_cn": MarketInfo(
            market_code="futures_cn",
            name="国内期货",
            symbol_model=FuturesVariety,
            daily_model=FuturesDaily,
            service_name="futures_daily_service",
            supports_multiple=False,
        ),
        "bond_cn": MarketInfo(
            market_code="bond_cn",
            name="国内债券",
            symbol_model=BondSymbol,
            daily_model=BondDaily,
            service_name="bond_daily_service",
            supports_multiple=True,
        ),
        "bond_us": MarketInfo(
            market_code="bond_us",
            name="美国债券",
            symbol_model=BondSymbol,
            daily_model=BondDaily,
            service_name="bond_daily_service",
            supports_multiple=True,
        ),
    }

    @classmethod
    def register(cls, market_info: MarketInfo) -> None:
        """注册新的市场."""
        cls._registry[market_info.market_code] = market_info

    @classmethod
    def get_info(cls, market_code: str) -> Optional[MarketInfo]:
        """获取市场信息."""
        return cls._registry.get(market_code)

    @classmethod
    def is_supported(cls, market_code: str) -> bool:
        """检查市场是否支持."""
        return market_code in cls._registry

    @classmethod
    def get_symbol_model(cls, market_code: str) -> Optional[Type]:
        """获取市场的标的模型类."""
        info = cls._registry.get(market_code)
        return info.symbol_model if info else None

    @classmethod
    def get_daily_model(cls, market_code: str) -> Optional[Type]:
        """获取市场的日线模型类."""
        info = cls._registry.get(market_code)
        return info.daily_model if info else None

    @classmethod
    def get_service_name(cls, market_code: str) -> Optional[str]:
        """获取市场的服务名称."""
        info = cls._registry.get(market_code)
        return info.service_name if info else None

    @classmethod
    def get_all_markets(cls) -> Dict[str, MarketInfo]:
        """获取所有已注册市场."""
        return cls._registry.copy()

    @classmethod
    def get_stock_markets(cls) -> list:
        """获取所有股票相关市场（A股/美股/港股共享StockSymbol/StockDaily）."""
        return ["stock_cn", "stock_us", "stock_hk"]

    @classmethod
    def get_bond_markets(cls) -> list:
        """获取所有债券相关市场."""
        return ["bond_cn", "bond_us"]

    @classmethod
    async def get_market_code_by_id(cls, market_id: UUID, db: AsyncSession) -> Optional[str]:
        """根据market_id获取market_code（异步DB查询）."""
        result = await db.execute(
            select(Market).where(Market.id == market_id)
        )
        market = result.scalar_one_or_none()
        return market.code if market else None


market_registry = MarketRegistry()