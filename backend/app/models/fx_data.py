"""
汇率数据模型.

定义fx_data表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-10 - 新增symbol_code、change_pct、change_amount、amplitude字段
"""

from sqlalchemy import Column, String, Date, Numeric, BigInteger, DateTime, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class FXData(Base):
    """
    汇率数据模型.

    Attributes:
        id: 数据ID（UUID）
        symbol: 货币对名称（中文，如"美元人民币"）
        symbol_code: 货币对代码（英文，如"USDCNY"）
        date: 交易日期
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量（外汇通常为0）
        change_pct: 涨跌幅(%)
        change_amount: 涨跌额
        amplitude: 振幅(%)
        created_at: 创建时间
    """
    __tablename__ = "fx_data"
    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uq_fx_data_symbol_date"),
        Index("idx_fx_data_symbol_code", "symbol_code"),
        Index("idx_fx_data_symbol_date", "symbol", "date"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(50), nullable=False, index=True)
    symbol_code = Column(String(20), nullable=False)  # 货币对英文代码
    date = Column(Date, nullable=False, index=True)
    open = Column(Numeric(10, 4))
    high = Column(Numeric(10, 4))
    low = Column(Numeric(10, 4))
    close = Column(Numeric(10, 4))
    volume = Column(BigInteger, default=0)  # 外汇数据volume为0
    change_pct = Column(Numeric(10, 4))  # 涨跌幅
    change_amount = Column(Numeric(10, 4))  # 涨跌额
    amplitude = Column(Numeric(10, 4))  # 振幅
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)