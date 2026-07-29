"""
宏观数据源配置 Pydantic Schema.

Author: FDAS Team
Created: 2026-07-29
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class MacroConfigCreate(BaseModel):
    """创建宏观数据源配置."""
    name: str = Field(..., description="数据源显示名称")
    source_code: str = Field(..., description="数据源代码")
    source_type: str = Field(..., description="数据源类型(excel/html/json/csv)")
    description: Optional[str] = Field(None, description="数据源描述")
    url: str = Field(..., description="数据源URL地址")
    parse_engine: str = Field(default="pandas", description="解析引擎")
    parse_config: dict = Field(default_factory=dict, description="解析规则配置")
    headers: Optional[dict] = Field(None, description="HTTP请求头")
    request_method: str = Field(default="GET", description="HTTP请求方法")
    timeout_seconds: int = Field(default=60, description="请求超时时间(秒)")
    retry_max_attempts: int = Field(default=3, description="最大重试次数")
    retry_backoff_factor: float = Field(default=2.0, description="重试退避因子")
    cron_expr: Optional[str] = Field(None, description="定时采集Cron表达式")
    is_enabled: bool = Field(default=True, description="是否启用")


class MacroConfigUpdate(BaseModel):
    """更新宏观数据源配置(所有字段可选)."""
    name: Optional[str] = Field(None, description="数据源显示名称")
    url: Optional[str] = Field(None, description="数据源URL地址")
    parse_engine: Optional[str] = Field(None, description="解析引擎")
    parse_config: Optional[dict] = Field(None, description="解析规则配置")
    headers: Optional[dict] = Field(None, description="HTTP请求头")
    request_method: Optional[str] = Field(None, description="HTTP请求方法")
    timeout_seconds: Optional[int] = Field(None, description="请求超时时间(秒)")
    retry_max_attempts: Optional[int] = Field(None, description="最大重试次数")
    retry_backoff_factor: Optional[float] = Field(None, description="重试退避因子")
    cron_expr: Optional[str] = Field(None, description="定时采集Cron表达式")
    is_enabled: Optional[bool] = Field(None, description="是否启用")


class MacroConfigResponse(BaseModel):
    """宏观数据源配置响应."""
    id: UUID
    name: str
    source_code: str
    source_type: str
    description: Optional[str]
    url: str
    parse_engine: str
    parse_config: dict
    headers: Optional[dict]
    request_method: str
    timeout_seconds: int
    retry_max_attempts: int
    retry_backoff_factor: float
    cron_expr: Optional[str]
    is_enabled: bool
    last_collected_at: Optional[datetime]
    last_status: Optional[str]
    last_message: Optional[str]
    last_records_count: int
    config_version: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MacroConfigListResponse(BaseModel):
    """宏观数据源配置列表响应."""
    success: bool = True
    data: list[MacroConfigResponse]
    total: int
