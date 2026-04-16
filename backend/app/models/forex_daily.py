"""
外汇日线行情模型.

定义forex_daily表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-10
Updated: 2026-04-11 - 新增volume字段
"""

from sqlalchemy import Column, String, Date, Numeric, DateTime, ForeignKey, UniqueConstraint, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class ForexDaily(Base):
    """
    外汇日线行情模型.

    存储外汇货币对的日线行情数据.
    注意：此表使用PostgreSQL分区，按年份分区.

    Attributes:
        id: 数据唯一标识ID（UUID）
        symbol_id: 关联货币对ID
        datasource_id: 数据来源ID
        date: 交易日期
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量（外汇数据通常为0）
        change_pct: 涨跌幅（百分比）
        change_amount: 涨跌额
        amplitude: 振幅（百分比）
        updated_at: 数据更新时间
    """
    __tablename__ = "forex_daily"
    __table_args__ = (
        UniqueConstraint("symbol_id", "date", "datasource_id", name="uq_forex_daily_symbol_date_datasource"),
        # PostgreSQL分区表，__table_args__中不能定义索引
        # 索引在init-db.sql中创建
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="数据唯一标识ID")
    symbol_id = Column(UUID(as_uuid=True), ForeignKey("forex_symbols.id"), nullable=False, comment="关联货币对ID")
    datasource_id = Column(UUID(as_uuid=True), ForeignKey("datasources.id"), comment="数据来源ID")
    date = Column(Date, nullable=False, comment="交易日期")
    open = Column(Numeric(10, 4), comment="开盘价")
    high = Column(Numeric(10, 4), comment="最高价")
    low = Column(Numeric(10, 4), comment="最低价")
    close = Column(Numeric(10, 4), comment="收盘价")
    volume = Column(BigInteger, default=0, comment="成交量（外汇数据通常为0）")
    change_pct = Column(Numeric(10, 4), comment="涨跌幅（百分比）")
    change_amount = Column(Numeric(10, 4), comment="涨跌额")
    amplitude = Column(Numeric(10, 4), comment="振幅（百分比）")
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="数据更新时间")