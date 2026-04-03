"""
汇率数据模型.

定义fx_data表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-03
"""

from sqlalchemy import Column, String, Date, Numeric, BigInteger, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class FXData(Base):
    """
    汇率数据模型.

    Attributes:
        id: 数据ID（UUID）
        symbol: 汇率符号（如USDCNH）
        date: 日期
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量
        created_at: 创建时间
    """
    __tablename__ = "fx_data"
    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uq_fx_data_symbol_date"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Numeric(10, 4))
    high = Column(Numeric(10, 4))
    low = Column(Numeric(10, 4))
    close = Column(Numeric(10, 4))
    volume = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)