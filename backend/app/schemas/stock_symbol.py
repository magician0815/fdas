"""
股票标的Schema.

定义股票标的基础信息相关的请求和响应模型.

Author: FDAS Team
Created: 2026-04-23
"""

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class StockSymbolBase(BaseModel):
    """股票标的基础模型."""
    code: str = Field(..., description="股票代码", max_length=20)
    name: str = Field(..., description="股票名称", max_length=100)
    exchange: Optional[str] = Field(None, description="交易所代码", max_length=20)
    industry: Optional[str] = Field(None, description="所属行业", max_length=50)
    is_active: bool = Field(default=True, description="是否启用")
    description: Optional[str] = Field(None, description="股票描述")


class StockSymbolCreate(StockSymbolBase):
    """创建股票标的请求."""
    market_id: Optional[UUID] = Field(None, description="所属市场ID")
    datasource_id: Optional[UUID] = Field(None, description="默认数据来源ID")
    listing_date: Optional[date] = Field(None, description="上市日期")


class StockSymbolUpdate(BaseModel):
    """更新股票标的请求."""
    name: Optional[str] = Field(None, description="股票名称", max_length=100)
    market_id: Optional[UUID] = Field(None, description="所属市场ID")
    exchange: Optional[str] = Field(None, description="交易所代码", max_length=20)
    industry: Optional[str] = Field(None, description="所属行业", max_length=50)
    datasource_id: Optional[UUID] = Field(None, description="默认数据来源ID")
    listing_date: Optional[date] = Field(None, description="上市日期")
    is_active: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, description="股票描述")


class StockSymbolResponse(BaseModel):
    """股票标的响应."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    market_id: Optional[UUID]
    exchange: Optional[str]
    industry: Optional[str]
    listing_date: Optional[date]
    datasource_id: Optional[UUID]
    is_active: bool
    description: Optional[str]
    created_at: date
    updated_at: date


class StockSymbolListItem(BaseModel):
    """股票标的列表项（简化版）."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    market_id: Optional[UUID]
    exchange: Optional[str]
    is_active: bool