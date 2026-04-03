"""
数据源模型.

定义datasources表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-03
"""

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.core.database import Base


class DataSource(Base):
    """
    数据源模型.

    Attributes:
        id: 数据源ID（UUID）
        name: 数据源名称
        type: 数据源类型（默认akshare）
        config: 配置参数（JSON）
        is_active: 是否激活
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "datasources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False, default="akshare")
    config = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)