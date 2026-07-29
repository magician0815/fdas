"""
宏观数据源配置模型.

Author: FDAS Team
Created: 2026-07-29
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone
import uuid

from app.core.database import Base


class MacroDataSourceConfig(Base):
    """宏观数据源配置模型."""

    __tablename__ = "macro_datasource_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="配置唯一标识ID")
    name = Column(String(100), nullable=False, unique=True, comment="数据源显示名称")
    source_code = Column(String(50), nullable=False, unique=True, comment="数据源代码")
    source_type = Column(String(30), nullable=False, comment="数据源类型(excel/html/json/csv)")
    description = Column(Text, comment="数据源描述说明")
    url = Column(Text, nullable=False, comment="数据源URL地址")
    parse_engine = Column(String(30), nullable=False, default="pandas", server_default="pandas", comment="解析引擎")
    parse_config = Column(JSONB, nullable=False, default=dict, server_default="{}", comment="解析规则配置(JSON对象)")
    headers = Column(JSONB, comment="HTTP请求头(JSON对象)")
    request_method = Column(String(10), default="GET", comment="HTTP请求方法")
    timeout_seconds = Column(Integer, default=60, comment="请求超时时间(秒)")
    retry_max_attempts = Column(Integer, default=3, comment="最大重试次数")
    retry_backoff_factor = Column(Float, default=2.0, comment="重试退避因子")
    cron_expr = Column(String(100), comment="定时采集Cron表达式")
    is_enabled = Column(Boolean, default=True, comment="是否启用定时采集")
    last_collected_at = Column(DateTime(timezone=True), comment="上次采集时间")
    last_status = Column(String(20), comment="上次采集状态")
    last_message = Column(Text, comment="上次采集消息")
    last_records_count = Column(Integer, default=0, comment="上次采集记录数")
    config_version = Column(String(20), default="1.0", comment="配置版本号")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), comment="更新时间")
