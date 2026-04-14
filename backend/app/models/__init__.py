"""
数据模型模块.

提供 SQLAlchemy ORM 模型定义.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-14 - 新增期货市场模型（品种、合约、日线）
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
]