"""
Session模型.

定义sessions表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-03
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.core.database import Base


class Session(Base):
    """
    Session模型.

    Attributes:
        id: Session ID（UUID）
        user_id: 用户ID（外键）
        session_data: Session数据（JSON）
        created_at: 创建时间
        expires_at: 过期时间
    """
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    session_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)