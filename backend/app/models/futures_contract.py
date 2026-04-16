"""
期货合约信息模型.

定义futures_contracts表的SQLAlchemy模型类.

期货合约是期货品种的具体月份合约，如：
- IF2401: 沪深300股指期货2024年1月合约
- IF2402: 沪深300股指期货2024年2月合约

Author: FDAS Team
Created: 2026-04-14
"""

from sqlalchemy import Column, String, Boolean, DateTime, Date, Text, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class FuturesContract(Base):
    """
    期货合约信息模型.

    存储期货合约的具体信息.

    Attributes:
        id: 合约唯一标识ID（UUID）
        variety_id: 关联品种ID
        contract_code: 合约代码（如IF2401）
        contract_name: 合约名称（如沪深300股指期货2401）
        contract_month: 合约月份（如2401表示2024年1月）
        year: 合约年份
        month: 合约月份（1-12）
        listing_date: 上市日期
        last_trade_date: 最后交易日/到期日
        delivery_date: 交割日
        is_main_contract: 是否为当前主力合约
        main_start_date: 成为主力合约的开始日期
        main_end_date: 作为主力合约的结束日期
        open_interest: 当前持仓量（用于主力合约判断）
        datasource_id: 数据来源ID
        is_active: 是否启用（已到期合约设为False）
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "futures_contracts"
    __table_args__ = (
        UniqueConstraint("contract_code", name="uq_futures_contracts_code"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="合约唯一标识ID")
    variety_id = Column(UUID(as_uuid=True), ForeignKey("futures_varieties.id"), nullable=False, index=True, comment="关联品种ID")
    contract_code = Column(String(20), unique=True, nullable=False, index=True, comment="合约代码（如IF2401）")
    contract_name = Column(String(100), nullable=False, comment="合约名称（如沪深300股指期货2401）")
    contract_month = Column(String(10), nullable=False, comment="合约月份标识（如2401）")
    year = Column(String(4), nullable=False, comment="合约年份")
    month = Column(String(2), nullable=False, comment="合约月份（01-12）")
    listing_date = Column(Date, comment="上市日期")
    last_trade_date = Column(Date, nullable=False, comment="最后交易日/到期日")
    delivery_date = Column(Date, comment="交割日")
    is_main_contract = Column(Boolean, default=False, index=True, comment="是否为当前主力合约")
    main_start_date = Column(Date, comment="成为主力合约的开始日期")
    main_end_date = Column(Date, comment="作为主力合约的结束日期")
    open_interest = Column(Numeric(20, 0), default=0, comment="当前持仓量")
    datasource_id = Column(UUID(as_uuid=True), ForeignKey("datasources.id"), index=True, comment="数据来源ID")
    is_active = Column(Boolean, default=True, index=True, comment="是否启用（已到期设为False）")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), comment="更新时间")