"""
用户模型.

定义users表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-03
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class User(Base):
    """
    用户模型.

    Attributes:
        id: 用户ID（UUID）
        username: 用户名（唯一）
        password_hash: 密码hash（bcrypt）
        role: 角色（admin/user）
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)