"""
采集任务模型.

定义collection_tasks表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-10 - 新增market_id、symbol_id字段，添加字段注释
"""

from sqlalchemy import Column, String, DateTime, Boolean, Date, ForeignKey, Integer, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class CollectionTask(Base):
    """
    采集任务模型.

    存储采集任务配置和执行状态.

    Attributes:
        id: 任务ID（UUID）
        name: 任务名称
        datasource_id: 数据源ID（外键）
        market_id: 目标市场类型ID
        symbol_id: 目标标的ID
        start_date: 采集开始日期
        end_date: 采集结束日期
        cron_expr: Cron表达式
        is_enabled: 是否启用
        last_run_at: 上次执行时间
        next_run_at: 下次执行时间
        last_status: 上次执行状态（success/failed/running）
        last_message: 上次执行消息
        last_records_count: 上次采集记录数
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "collection_tasks"
    __table_args__ = (
        Index("idx_collection_tasks_datasource", "datasource_id"),
        Index("idx_collection_tasks_market", "market_id"),
        Index("idx_collection_tasks_enabled", "is_enabled"),
        Index("idx_collection_tasks_next_run", "next_run_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="任务唯一标识ID")
    name = Column(String(100), nullable=False, comment="任务名称")
    datasource_id = Column(
        UUID(as_uuid=True),
        ForeignKey("datasources.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联数据源ID"
    )
    market_id = Column(
        UUID(as_uuid=True),
        ForeignKey("markets.id"),
        nullable=False,
        comment="目标市场类型ID"
    )
    symbol_id = Column(UUID(as_uuid=True), nullable=False, comment="目标标的ID")
    start_date = Column(Date, comment="采集开始日期")
    end_date = Column(Date, comment="采集结束日期")
    cron_expr = Column(String(100), comment="Cron定时表达式")
    is_enabled = Column(Boolean, default=False, comment="是否启用")
    last_run_at = Column(DateTime(timezone=True), comment="上次执行时间")
    next_run_at = Column(DateTime(timezone=True), comment="下次执行时间")
    last_status = Column(String(20), comment="上次执行状态")
    last_message = Column(Text, comment="上次执行消息")
    last_records_count = Column(Integer, default=0, comment="上次采集记录数")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")