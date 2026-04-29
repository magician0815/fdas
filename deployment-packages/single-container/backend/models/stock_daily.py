"""
股票日线行情模型.

定义stock_daily表的SQLAlchemy模型类，支持A股/美股/港股共享.
注意：此表使用PostgreSQL分区，按年份分区.

Author: FDAS Team
Created: 2026-04-23
"""

from sqlalchemy import Column, String, Date, Numeric, DateTime, ForeignKey, UniqueConstraint, BigInteger, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class StockDaily(Base):
    """
    股票日线行情模型.

    存储股票的日线行情数据，支持A股/美股/港股共享此表.
    注意：此表使用PostgreSQL分区，按年份分区.

    Attributes:
        id: 数据唯一标识ID（UUID）
        symbol_id: 关联股票ID（外键到stock_symbols表）
        market_id: 所属市场ID（外键到markets表，用于区分A股/美股/港股）
        datasource_id: 数据来源ID
        date: 交易日期
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量
        amount: 成交额
        turnover: ��手率（百分比）
        change_pct: 涨跌幅（百分比）
        change_amount: 涨跌额
        amplitude: 振幅（百分比）
        is_suspended: 是否停牌
        is_st: 是否ST股票
        updated_at: 数据更新时间
    """
    __tablename__ = "stock_daily"
    __table_args__ = (
        UniqueConstraint("symbol_id", "market_id", "date", "datasource_id", name="stock_daily_symbol_market_date_datasource_key"),
        # PostgreSQL分区表，主键必须包含分区键(date)
        {"primary_key": ["id", "date"]}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="数据唯一标识ID")
    symbol_id = Column(UUID(as_uuid=True), ForeignKey("stock_symbols.id"), nullable=False, comment="关联股票ID")
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id"), nullable=False, index=True, comment="所属市场ID")
    datasource_id = Column(UUID(as_uuid=True), ForeignKey("datasources.id"), comment="数据来源ID")
    date = Column(Date, primary_key=True, nullable=False, comment="交易日期")
    open = Column(Numeric(10, 4), comment="开盘价")
    high = Column(Numeric(10, 4), comment="��高价")
    low = Column(Numeric(10, 4), comment="最低价")
    close = Column(Numeric(10, 4), comment="收盘价")
    volume = Column(BigInteger, default=0, comment="成交量")
    amount = Column(Numeric(20, 2), default=0, comment="成交额")
    turnover = Column(Numeric(10, 4), nullable=True, comment="换手率（百分比）")
    change_pct = Column(Numeric(10, 4), nullable=True, comment="涨跌幅（百分比）")
    change_amount = Column(Numeric(10, 4), nullable=True, comment="涨跌额")
    amplitude = Column(Numeric(10, 4), nullable=True, comment="振幅（百分比）")
    is_suspended = Column(Boolean, default=False, comment="是否停牌")
    is_st = Column(Boolean, default=False, comment="是否ST股票")
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="数据更新时间")