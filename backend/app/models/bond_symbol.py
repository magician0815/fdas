"""
债券标的基础信息模型.

定义bond_symbols表的SQLAlchemy模型类，支持国内/国际债券共享.

Author: FDAS Team
Created: 2026-04-23
"""

from sqlalchemy import Column, String, Boolean, DateTime, Date, Text, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class BondSymbol(Base):
    """
    债券标的基础信息模型.

    存储债券的基础信息，支持国内/国际债券共享此表.

    Attributes:
        id: 债券唯一标识ID（UUID）
        code: 债券代码
        name: 债券名称
        market_id: 所属市场ID（外键到markets表）
        bond_type: 债券类型（国债/企业债/可转债/金融债）
        issuer: 发行人
        coupon_rate: 票面利率（百分比）
        maturity_date: 到期日期
        face_value: 面值
        currency: 币种
        rating: 信用评级
        datasource_id: 默认数据来源ID
        is_active: 是否启用
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "bond_symbols"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="债券唯一标识ID")
    code = Column(String(20), unique=True, nullable=False, index=True, comment="债券代码")
    name = Column(String(100), nullable=False, comment="债券名称")
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id"), nullable=True, index=True, comment="所属市场ID")
    bond_type = Column(String(20), nullable=False, comment="债券类型（国债/企业债/可转债/金融债）")
    issuer = Column(String(100), nullable=True, comment="发行人")
    coupon_rate = Column(Numeric(10, 4), nullable=True, comment="票面利率（百分比）")
    maturity_date = Column(Date, nullable=True, comment="到期日期")
    face_value = Column(Numeric(12, 2), default=100.00, comment="面值")
    currency = Column(String(10), default="CNY", comment="币种")
    rating = Column(String(10), nullable=True, comment="信用评级")
    datasource_id = Column(UUID(as_uuid=True), ForeignKey("datasources.id", ondelete="SET NULL"), nullable=True, comment="数据源ID")
    is_active = Column(Boolean, default=True, comment="是否启用")
    description = Column(Text, nullable=True, comment="债券描述")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), comment="更新时间")