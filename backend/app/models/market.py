"""
市场类型模型.

定义markets表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-10
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class Market(Base):
    """
    市场类型模型.

    定义不同市场类型（外汇、A股、美股等）.

    Attributes:
        id: 市场唯一标识ID（UUID）
        code: 市场代码（如forex, stock_cn）
        name: 市场名称（如外汇, A股）
        description: 市场描述
        timezone: 市场交易时区
        is_active: 是否启用
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "markets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="市场唯一标识ID")
    code = Column(String(20), unique=True, nullable=False, index=True, comment="市场代码")
    name = Column(String(50), nullable=False, comment="市场名称")
    description = Column(Text, comment="市场描述说明")
    timezone = Column(String(50), default="Asia/Shanghai", comment="市场交易时区")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")