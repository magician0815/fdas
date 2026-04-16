"""
期货品种基础信息模型.

定义futures_varieties表的SQLAlchemy模型类.

期货品种是指期货交易的标的品种，如：
- IF: 沪深300股指期货
- IC: 中证500股指期货
- IH: 上证50股指期货
- AU: 黄金期货
- CU: 铜期货

Author: FDAS Team
Created: 2026-04-14
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class FuturesVariety(Base):
    """
    期货品种基础信息模型.

    存储期货品种的基础信息.

    Attributes:
        id: 品种唯一标识ID（UUID）
        code: 品种代码（如IF、IC、AU）
        name: 品种名称（如沪深300股指期货）
        exchange: 交易所代码（CFFEX、SHFE、DCE、CZCE）
        market_id: 所属市场ID
        contract_unit: 合约单位（如IF为300元/点）
        min_price_tick: 最小变动价位
        trading_months: 交易月份（如1,3,5,7,9,11）
        delivery_months: 交割月份规则
        delivery_method: 交割方式（现金交割/实物交割）
        last_trade_day_rule: 最后交易日规则
        description: 品种描述
        is_active: 是否启用
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "futures_varieties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="品种唯一标识ID")
    code = Column(String(20), unique=True, nullable=False, index=True, comment="品种代码")
    name = Column(String(100), nullable=False, comment="品种名称")
    exchange = Column(String(20), nullable=False, index=True, comment="交易所代码（CFFEX/SHFE/DCE/CZCE）")
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id"), index=True, comment="所属市场ID")
    contract_unit = Column(Numeric(10, 2), comment="合约单位（元/点或吨/手）")
    min_price_tick = Column(Numeric(10, 4), comment="最小变动价位")
    trading_months = Column(String(50), comment="交易月份规则（如1,3,5,7,9,11）")
    delivery_months = Column(String(50), comment="交割月份规则")
    delivery_method = Column(String(20), comment="交割方式（cash_delivery/physical_delivery）")
    last_trade_day_rule = Column(Text, comment="最后交易日规则描述")
    description = Column(Text, comment="品种描述说明")
    is_active = Column(Boolean, default=True, index=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), comment="更新时间")