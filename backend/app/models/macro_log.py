"""
宏观采集日志模型.

Author: FDAS Team
Created: 2026-07-29
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class MacroCollectionLog(Base):
    """宏观数据采集执行日志模型."""

    __tablename__ = "macro_collection_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="日志唯一标识ID")
    config_id = Column(UUID(as_uuid=True), ForeignKey("macro_datasource_configs.id", ondelete="CASCADE"), nullable=False, comment="关联配置ID")
    run_at = Column(DateTime(timezone=True), nullable=False, comment="执行时间")
    status = Column(String(20), nullable=False, comment="执行状态(success/failed/partial/running)")
    records_count = Column(Integer, default=0, comment="采集记录数")
    message = Column(Text, comment="执行消息")
    duration_ms = Column(Integer, comment="执行耗时(毫秒)")
    is_full = Column(Boolean, default=False, comment="是否全量采集")
    error_detail = Column(Text, comment="错误详情")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="创建时间")
