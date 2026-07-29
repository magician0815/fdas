"""
宏观数据点模型.

Author: FDAS Team
Created: 2026-07-29
"""

from sqlalchemy import Column, String, DateTime, Date, Boolean, Text, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class MacroDataPoint(Base):
    """宏观数据点模型(按publish_date分区)."""

    __tablename__ = "macro_data_points"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, comment="数据唯一标识ID")
    config_id = Column(UUID(as_uuid=True), ForeignKey("macro_datasource_configs.id", ondelete="CASCADE"), nullable=False, comment="关联配置ID")
    source_code = Column(String(50), nullable=False, comment="数据源代码")
    country = Column(String(30), comment="国家/地区")
    series_name = Column(String(200), nullable=False, comment="数据系列名称")
    indicator_key = Column(String(100), nullable=False, comment="指标键名")
    value = Column(Numeric(20, 10), comment="数值")
    publish_date = Column(Date, nullable=False, primary_key=True, comment="发布日期(分区键)")
    period_date = Column(Date, comment="数据所属期间日期")
    frequency = Column(String(20), default="quarterly", comment="数据频率")
    forecast_year = Column(Integer, comment="预测年份(SEP数据专用)")
    unit = Column(String(50), comment="单位")
    extra_info = Column("metadata", JSONB, default=dict, comment="元数据")
    raw_source_hash = Column(String(64), comment="原始数据行哈希(用于增量去重)")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="创建时间")
