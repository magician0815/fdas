"""测算规则定义模型."""

from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class MacroCalculationRule(Base):
    """测算规则定义."""

    __tablename__ = "macro_calculation_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="规则唯一标识ID")
    rule_code = Column(String(50), nullable=False, unique=True, comment="规则编码")
    rule_name = Column(String(100), nullable=False, comment="规则名称")
    description = Column(Text, comment="规则描述说明")
    formula_latex = Column(Text, nullable=False, comment="LaTeX格式公式")
    variables_config = Column(JSONB, nullable=False, default=dict, comment="变量定义及绑定配置")
    constants_config = Column(JSONB, nullable=False, default=dict, comment="常量及系数配置")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), comment="更新时间")
