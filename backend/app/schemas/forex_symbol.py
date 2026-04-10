"""
外汇标的Schema.

定义外汇标的基础信息相关的请求和响应模型.

Author: FDAS Team
Created: 2026-04-10
"""

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field
from uuid import UUID


class ForexSymbolBase(BaseModel):
    """外汇标的基础模型."""
    code: str = Field(..., description="货币对代码（英文，如USDCNY）", max_length=20)
    name: str = Field(..., description="货币对名称（中文，如美元人民币）", max_length=50)
    description: Optional[str] = Field(None, description="货币对描述")
    base_currency: Optional[str] = Field(None, description="基础货币", max_length=10)
    quote_currency: Optional[str] = Field(None, description="计价货币", max_length=10)
    is_active: bool = Field(default=True, description="是否启用")


class ForexSymbolCreate(ForexSymbolBase):
    """创建外汇标的请求."""
    datasource_id: Optional[UUID] = Field(None, description="默认数据来源ID")
    first_trade_date: Optional[date] = Field(None, description="首次交易日期")


class ForexSymbolUpdate(BaseModel):
    """更新外汇标的请求."""
    name: Optional[str] = Field(None, description="货币对名称", max_length=50)
    description: Optional[str] = Field(None, description="货币对描述")
    datasource_id: Optional[UUID] = Field(None, description="默认数据来源ID")
    base_currency: Optional[str] = Field(None, description="基础货币", max_length=10)
    quote_currency: Optional[str] = Field(None, description="计价货币", max_length=10)
    is_active: Optional[bool] = Field(None, description="是否启用")
    first_trade_date: Optional[date] = Field(None, description="首次交易日期")


class ForexSymbolResponse(BaseModel):
    """外汇标的响应."""
    id: UUID
    code: str
    name: str
    description: Optional[str]
    datasource_id: Optional[UUID]
    base_currency: Optional[str]
    quote_currency: Optional[str]
    is_active: bool
    first_trade_date: Optional[date]
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


class ForexSymbolListItem(BaseModel):
    """外汇标的列表项（简化版）."""
    id: UUID
    code: str
    name: str
    base_currency: Optional[str]
    quote_currency: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True