"""测算结果模型."""

from sqlalchemy import Column, String, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class MacroCalculationResult(Base):
    """测算结果."""

    __tablename__ = "macro_calculation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="结果唯一标识ID")
    rule_id = Column(UUID(as_uuid=True), ForeignKey("macro_calculation_rules.id", ondelete="CASCADE"), nullable=False, comment="关联规则ID")
    rule_code = Column(String(50), nullable=False, comment="规则编码")
    result_value = Column(Numeric(10, 4), comment="计算结果值")
    result_period = Column(Date, comment="结果所属期间")
    variable_snapshot = Column(JSONB, nullable=False, default=dict, comment="变量取值快照(JSON)")
    calculation_process = Column(JSONB, nullable=False, default=dict, comment="计算步骤详情(JSON)")
    rule_snapshot = Column(JSONB, nullable=False, default=dict, comment="规则配置快照(JSON)")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="计算时间")
