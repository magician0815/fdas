"""
期货日线行情模型.

定义futures_daily表的SQLAlchemy模型类.

期货日线行情包含OHLC数据以及期货特有的持仓量(OI)数据.

Author: FDAS Team
Created: 2026-04-14
"""

from sqlalchemy import Column, String, Date, Numeric, DateTime, ForeignKey, UniqueConstraint, BigInteger, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class FuturesDaily(Base):
    """
    期货日线行情模型.

    存储期货合约的日线行情数据.
    注意：此表使用PostgreSQL分区，按年份分区.

    Attributes:
        id: 数据唯一标识ID（UUID）
        contract_id: 关联合约ID
        variety_id: 关联品种ID（方便查询品种数据）
        datasource_id: 数据来源ID
        date: 交易日期
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量
        open_interest: 持仓量（期货特有指标）
        settle_price: 结算价（期货特有价格）
        turnover: 成交金额
        change_pct: 涨跌幅（百分比）
        change_amount: 涨跌额
        amplitude: 挰幅（百分比）
        oi_change: 持仓量变化
        is_main_data: 是否为主力合约数据（用于主力连续拼接）
        adjusted_price: 调整后价格（挢月平滑处理后）
        updated_at: 数据更新时间
    """
    __tablename__ = "futures_daily"
    __table_args__ = (
        UniqueConstraint("contract_id", "date", "datasource_id", name="uq_futures_daily_contract_date_datasource"),
        # PostgreSQL分区表，索引在init-db.sql中创建
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="数据唯一标识ID")
    contract_id = Column(UUID(as_uuid=True), ForeignKey("futures_contracts.id"), nullable=False, comment="关联合约ID")
    variety_id = Column(UUID(as_uuid=True), ForeignKey("futures_varieties.id"), nullable=False, index=True, comment="关联品种ID")
    datasource_id = Column(UUID(as_uuid=True), ForeignKey("datasources.id"), comment="数据来源ID")
    date = Column(Date, nullable=False, comment="交易日期")
    open = Column(Numeric(10, 4), comment="开盘价")
    high = Column(Numeric(10, 4), comment="最高价")
    low = Column(Numeric(10, 4), comment="最低价")
    close = Column(Numeric(10, 4), comment="收盘价")
    settle_price = Column(Numeric(10, 4), comment="结算价")
    volume = Column(BigInteger, default=0, comment="成交量")
    open_interest = Column(BigInteger, default=0, comment="持仓量（OI）")
    turnover = Column(Numeric(20, 2), default=0, comment="成交金额")
    change_pct = Column(Numeric(10, 4), comment="涨跌幅（百分比）")
    change_amount = Column(Numeric(10, 4), comment="涨跌额")
    amplitude = Column(Numeric(10, 4), comment="振幅（百分比）")
    oi_change = Column(BigInteger, default=0, comment="持仓量变化")
    is_main_data = Column(Boolean, default=False, index=True, comment="是否为主力合约数据")
    adjusted_price = Column(Numeric(10, 4), comment="挢月调整后价格")
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, comment="数据更新时间")