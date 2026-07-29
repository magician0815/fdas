"""
数据模型模块.

提供 SQLAlchemy ORM 模型定义.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-23 - 新增股票/债券市场模型
"""

from app.core.database import Base
from app.models.user import User
from app.models.session import Session
from app.models.market import Market
from app.models.datasource import DataSource
from app.models.collection_task import CollectionTask
from app.models.collection_task_log import CollectionTaskLog
from app.models.forex_symbol import ForexSymbol
from app.models.forex_daily import ForexDaily
from app.models.forex_intraday import ForexIntraday
from app.models.user_chart_setting import UserChartSetting
from app.models.futures_variety import FuturesVariety
from app.models.futures_contract import FuturesContract
from app.models.futures_daily import FuturesDaily
from app.models.stock_symbol import StockSymbol
from app.models.stock_daily import StockDaily
from app.models.bond_symbol import BondSymbol
from app.models.bond_daily import BondDaily
from app.models.macro_config import MacroDataSourceConfig
from app.models.macro_data import MacroDataPoint
from app.models.macro_log import MacroCollectionLog

__all__ = [
    "Base",
    "User",
    "Session",
    "Market",
    "DataSource",
    "CollectionTask",
    "CollectionTaskLog",
    "ForexSymbol",
    "ForexDaily",
    "ForexIntraday",
    "UserChartSetting",
    "FuturesVariety",
    "FuturesContract",
    "FuturesDaily",
    "StockSymbol",
    "StockDaily",
    "BondSymbol",
    "BondDaily",
    "MacroDataSourceConfig",
    "MacroDataPoint",
    "MacroCollectionLog",
]