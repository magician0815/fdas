"""
采集任务执行日志模型.

定义collection_task_logs表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-10
"""

from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class CollectionTaskLog(Base):
    """
    采集任务执行日志模型.

    Attributes:
        id: 日志ID（UUID）
        task_id: 任务ID（外键）
        run_at: 执行时间
        status: 执行状态（success/failed/running）
        records_count: 采集记录数
        message: 执行消息/错误信息
        duration_ms: 执行耗时（毫秒）
        created_at: 创建时间
    """
    __tablename__ = "collection_task_logs"
    __table_args__ = (
        Index("idx_task_logs_task", "task_id"),
        Index("idx_task_logs_run_at", "run_at"),
        Index("idx_task_logs_status", "status"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("collection_tasks.id", ondelete="CASCADE"),
        nullable=False
    )
    run_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False)  # success/failed/running
    records_count = Column(Integer, default=0)
    message = Column(Text)
    duration_ms = Column(Integer)  # 执行耗时（毫秒）
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)