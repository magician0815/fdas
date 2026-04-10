"""
数据源模型.

定义datasources表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-10 - 新增interface、config_schema、supported_symbols、min_date字段
"""

from sqlalchemy import Column, String, DateTime, Boolean, Date, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.core.database import Base


class DataSource(Base):
    """
    数据源模型.

    Attributes:
        id: 数据源ID（UUID）
        name: 数据源名称（唯一）
        interface: AKShare接口名称（如forex_hist）
        description: 数据源描述
        config_schema: 配置参数Schema（JSON，用于前端动态渲染表单）
        supported_symbols: 支持的货币对列表（JSON，可手工更新或自动获取）
        min_date: 接口最早可用数据日期
        type: 数据源类型（默认akshare）
        is_active: 是否启用
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "datasources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    interface = Column(String(50), nullable=False)  # AKShare接口名称
    description = Column(Text)  # 数据源描述
    config_schema = Column(JSONB, nullable=False)  # 配置参数Schema
    supported_symbols = Column(JSONB)  # 支持的货币对列表
    min_date = Column(Date)  # 接口最早可用数据日期
    type = Column(String(50), nullable=False, default="akshare")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)