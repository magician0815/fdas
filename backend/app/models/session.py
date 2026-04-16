"""
Session模型.

定义sessions表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-10 - 添加字段注释
Updated: 2026-04-16 - 添加IP绑定字段（安全增强）
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class Session(Base):
    """
    Session模型.

    存储用户登录会话信息.

    Attributes:
        id: Session ID（UUID）
        user_id: 用户ID（外键）
        session_data: Session数据（JSON）
        ip_address: 创建时的IP地址（可选安全验证）
        created_at: 创建时间
        expires_at: 过期时间
    """
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="会话唯一标识ID")
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联用户ID"
    )
    session_data = Column(JSONB, nullable=False, comment="会话数据")
    ip_address = Column(String(45), nullable=True, comment="创建会话时的IP地址（IPv4/IPv6）")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="创建时间")
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True, comment="过期时间")