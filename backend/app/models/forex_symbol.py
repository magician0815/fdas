"""
外汇标的基础信息模型.

定义forex_symbols表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-10
"""

from sqlalchemy import Column, String, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class ForexSymbol(Base):
    """
    外汇标的基础信息模型.

    存储外汇货币对的基础信息.

    Attributes:
        id: 货币对唯一标识ID（UUID）
        code: 货币对代码（英文，如USDCNY）
        name: 货币对名称（中文，如美元人民币）
        description: 货币对描述
        datasource_id: 默认数据来源ID
        base_currency: 基础货币（USD）
        quote_currency: 计价货币（CNY）
        is_active: 是否启用
        first_trade_date: 首次交易日期
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "forex_symbols"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="货币对唯一标识ID")
    code = Column(String(20), unique=True, nullable=False, index=True, comment="货币对代码（英文）")
    name = Column(String(50), nullable=False, comment="货币对名称（中文）")
    description = Column(Text, comment="货币对描述说明")
    datasource_id = Column(UUID(as_uuid=True), ForeignKey("datasources.id"), index=True, comment="默认数据来源ID")
    base_currency = Column(String(10), comment="基础货币")
    quote_currency = Column(String(10), comment="计价货币")
    is_active = Column(Boolean, default=True, index=True, comment="是否启用")
    first_trade_date = Column(Date, comment="首次交易日期")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")