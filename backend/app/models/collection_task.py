"""
采集任务模型.

定义collection_tasks表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-03
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class CollectionTask(Base):
    """
    采集任务模型.

    Attributes:
        id: 任务ID（UUID）
        name: 任务名称
        datasource_id: 数据源ID（外键）
        target_data: 目标数据字段
        cron_expression: cron表达式
        is_active: 是否激活
        last_run_at: 上次执行时间
        next_run_at: 下次执行时间
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "collection_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    datasource_id = Column(
        UUID(as_uuid=True),
        ForeignKey("datasources.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    target_data = Column(String(100), nullable=False)
    cron_expression = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True))
    next_run_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)