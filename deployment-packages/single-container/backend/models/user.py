"""
用户模型.

定义users表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-10 - 添加字段注释
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class User(Base):
    """
    用户模型.

    存储用户账户信息.

    Attributes:
        id: 用户ID（UUID）
        username: 用户名（唯一）
        password_hash: 密码hash（bcrypt）
        role: 角色（admin/user）
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="用户唯一标识ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值")
    role = Column(String(20), nullable=False, default="user", comment="用户角色")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), comment="更新时间")