"""
用户图表配置模型.

定义user_chart_settings表的SQLAlchemy模型类.

Author: FDAS Team
Created: 2026-04-11
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.core.database import Base


class UserChartSetting(Base):
    """
    用户图表配置模型.

    存储用户图表个性化配置（画线工具设置、主题偏好等）.

    Attributes:
        id: 配置记录唯一标识ID（UUID）
        user_id: 关联用户ID
        setting_type: 配置类型（drawing_tools/theme/indicators/view）
        setting_key: 配置键名
        setting_value: 配置值（JSON格式）
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "user_chart_settings"
    __table_args__ = (
        UniqueConstraint("user_id", "setting_type", "setting_key", name="uq_user_chart_settings_user_type_key"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="配置记录唯一标识ID")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="关联用户ID")
    setting_type = Column(String(50), nullable=False, comment="配置类型（drawing_tools/theme/indicators/view）")
    setting_key = Column(String(100), nullable=False, comment="配置键名")
    setting_value = Column(JSONB, nullable=False, comment="配置值（JSON格式）")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")