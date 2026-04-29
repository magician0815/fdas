"""
外汇分钟级行情模型.

定义forex_intraday表的SQLAlchemy模型类，存储分钟级K线数据.

Author: FDAS Team
Created: 2026-04-14
"""

from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, UniqueConstraint, BigInteger, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class ForexIntraday(Base):
    """
    外汇分钟级行情模型.

    存储外汇货币对的分钟级K线数据.
    注意：此表使用PostgreSQL分区，按月份分区.

    Attributes:
        id: 数据唯一标识ID（UUID）
        symbol_id: 关联货币对ID
        datasource_id: 数据来源ID
        timestamp: 数据时间戳（精确到分钟）
        interval: 时间间隔（1/5/15/30/60分钟）
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量（外汇数据通常为0）
        updated_at: 数据更新时间
    """
    __tablename__ = "forex_intraday"
    __table_args__ = (
        UniqueConstraint("symbol_id", "timestamp", "interval", "datasource_id", name="uq_forex_intraday_symbol_time_interval"),
        Index("idx_forex_intraday_symbol_time", "symbol_id", "timestamp"),
        Index("idx_forex_intraday_time", "timestamp"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="数据唯一标识ID")
    symbol_id = Column(UUID(as_uuid=True), ForeignKey("forex_symbols.id"), nullable=False, comment="关联货币对ID")
    datasource_id = Column(UUID(as_uuid=True), ForeignKey("datasources.id"), comment="数据来源ID")
    timestamp = Column(DateTime(timezone=True), nullable=False, comment="数据时间戳（精确到分钟）")
    interval = Column(String(10), nullable=False, default="1", comment="时间间隔（1/5/15/30/60分钟）")
    open = Column(Numeric(10, 4), comment="开盘价")
    high = Column(Numeric(10, 4), comment="最高价")
    low = Column(Numeric(10, 4), comment="最低价")
    close = Column(Numeric(10, 4), comment="收盘价")
    volume = Column(BigInteger, default=0, comment="成交量（外汇数据通常为0）")
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="数据更新时间")

    def to_dict(self):
        """转换为字典格式.

        Returns:
            dict: 数据字典
        """
        return {
            "id": str(self.id) if self.id else None,
            "symbol_id": str(self.symbol_id) if self.symbol_id else None,
            "datasource_id": str(self.datasource_id) if self.datasource_id else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "interval": self.interval,
            "open": float(self.open) if self.open else None,
            "high": float(self.high) if self.high else None,
            "low": float(self.low) if self.low else None,
            "close": float(self.close) if self.close else None,
            "volume": self.volume,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }