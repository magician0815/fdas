"""
股票标的基础信息模型.

定义stock_symbols表的SQLAlchemy模型类，支持A股/美股/港股共享.

Author: FDAS Team
Created: 2026-04-22
Updated: 2026-04-23 - 新增market_id字段支持多市场
"""

from sqlalchemy import Column, String, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class StockSymbol(Base):
    """
    股票标的基础信息模型.

    存储股票的基础信息，支持A股/美股/港股共享此表.

    Attributes:
        id: 股票唯一标识ID（UUID）
        code: 股票代码（如600519, AAPL, 00700）
        name: 股票名称
        market_id: 所属市场ID（外键到markets表）
        exchange: 交易所代码（如SSE, NASDAQ, HKEX）
        industry: 所属行业
        listing_date: 上市日期
        datasource_id: 默认数据来源ID
        is_active: 是否启用
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "stock_symbols"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="股票唯一标识ID")
    code = Column(String(20), unique=True, nullable=False, index=True, comment="股票代码")
    name = Column(String(100), nullable=False, comment="股票名称")
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id"), nullable=True, index=True, comment="所属市场ID")
    exchange = Column(String(20), nullable=True, comment="交易所代码")
    industry = Column(String(50), nullable=True, comment="所属行业")
    listing_date = Column(Date, nullable=True, comment="上市日期")
    datasource_id = Column(UUID(as_uuid=True), ForeignKey("datasources.id", ondelete="SET NULL"), nullable=True, comment="数据源ID")
    is_active = Column(Boolean, default=True, comment="是否启用")
    description = Column(Text, nullable=True, comment="股票描述")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), comment="更新时间")