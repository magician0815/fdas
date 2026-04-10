"""
采集任务执行日志模型.

定义collection_task_logs表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-10
Updated: 2026-04-10 - 添加字段注释
"""

from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class CollectionTaskLog(Base):
    """
    采集任务执行日志模型.

    记录采集任务的每次执行情况.

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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="日志唯一标识ID")
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("collection_tasks.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联任务ID"
    )
    run_at = Column(DateTime(timezone=True), nullable=False, comment="执行时间")
    status = Column(String(20), nullable=False, comment="执行状态")
    records_count = Column(Integer, default=0, comment="采集记录数")
    message = Column(Text, comment="执行消息或错误信息")
    duration_ms = Column(Integer, comment="执行耗时（毫秒）")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, comment="创建时间")