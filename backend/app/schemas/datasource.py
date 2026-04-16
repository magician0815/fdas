"""
数据源Schema.

定义数据源相关的请求和响应模型.

Author: FDAS Team
Created: 2026-04-10
Updated: 2026-04-10 - 适配market_id新字段
"""

from typing import Optional, List, Dict, Any
from datetime import date
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class DataSourceBase(BaseModel):
    """数据源基础模型."""
    name: str = Field(..., description="数据源名称", max_length=100)
    interface: str = Field(..., description="AKShare接口名称", max_length=50)
    description: Optional[str] = Field(None, description="数据源描述")
    config_schema: Dict[str, Any] = Field(..., description="配置参数Schema")
    supported_symbols: Optional[List[str]] = Field(None, description="支持的货币对列表")
    min_date: Optional[date] = Field(None, description="最早可用数据日期")
    type: str = Field(default="akshare", description="数据源类型", max_length=50)
    is_active: bool = Field(default=True, description="是否启用")


class DataSourceCreate(DataSourceBase):
    """创建数据源请求."""
    market_id: Optional[UUID] = Field(None, description="适用市场类型ID")


class DataSourceUpdate(BaseModel):
    """更新数据源请求."""
    name: Optional[str] = Field(None, description="数据源名称", max_length=100)
    market_id: Optional[UUID] = Field(None, description="适用市场类型ID")
    interface: Optional[str] = Field(None, description="AKShare接口名称", max_length=50)
    description: Optional[str] = Field(None, description="数据源描述")
    config_schema: Optional[Dict[str, Any]] = Field(None, description="配置参数Schema")
    supported_symbols: Optional[List[str]] = Field(None, description="支持的货币对列表")
    min_date: Optional[date] = Field(None, description="最早可用数据日期")
    is_active: Optional[bool] = Field(None, description="是否启用")


class DataSourceResponse(BaseModel):
    """数据源响应."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    market_id: Optional[UUID]
    interface: str
    description: Optional[str]
    config_schema: Dict[str, Any]
    supported_symbols: Optional[List[str]]
    min_date: Optional[date]
    type: str
    is_active: bool
    created_at: date
    updated_at: date


class SymbolInfo(BaseModel):
    """货币对信息."""
    value: str = Field(..., description="货币对名称（中文）")
    code: str = Field(..., description="货币对代码（英文）")
    label: str = Field(..., description="显示标签")


class SupportedSymbolsResponse(BaseModel):
    """支持的货币对响应."""
    datasource_id: UUID
    datasource_name: str
    current_symbols: Optional[List[str]]
    fetched_symbols: List[SymbolInfo]
    has_changes: bool = Field(..., description="是否有变更")
    added: List[str] = Field(default=[], description="新增的货币对")
    removed: List[str] = Field(default=[], description="移除的货币对")