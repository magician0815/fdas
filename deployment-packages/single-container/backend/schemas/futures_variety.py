"""
期货品种Schema.

定义期货品种基础信息相关的请求和响应模型.

Author: FDAS Team
Created: 2026-04-23
"""

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from decimal import Decimal


class FuturesVarietyBase(BaseModel):
    """期货品种基础模型."""
    code: str = Field(..., description="品种代码（如IF、IC、AU）", max_length=20)
    name: str = Field(..., description="品种名称（如沪深300股指期货）", max_length=100)
    exchange: str = Field(..., description="交易所代码（CFFEX/SHFE/DCE/CZCE）", max_length=20)
    is_active: bool = Field(default=True, description="是否启用")
    description: Optional[str] = Field(None, description="品种描述")


class FuturesVarietyCreate(FuturesVarietyBase):
    """创建期货品种请求."""
    market_id: Optional[UUID] = Field(None, description="所属市场ID")
    contract_unit: Optional[Decimal] = Field(None, description="合约单位（元/点或吨/手）")
    min_price_tick: Optional[Decimal] = Field(None, description="最小变动价位")
    trading_months: Optional[str] = Field(None, description="交易月份规则", max_length=50)
    delivery_months: Optional[str] = Field(None, description="交割月份规则", max_length=50)
    delivery_method: Optional[str] = Field(None, description="交割方式", max_length=20)
    last_trade_day_rule: Optional[str] = Field(None, description="最后交易日规则描述")


class FuturesVarietyUpdate(BaseModel):
    """更新期货品种请求."""
    name: Optional[str] = Field(None, description="品种名称", max_length=100)
    exchange: Optional[str] = Field(None, description="交易所代码", max_length=20)
    market_id: Optional[UUID] = Field(None, description="所属市场ID")
    contract_unit: Optional[Decimal] = Field(None, description="合约单位")
    min_price_tick: Optional[Decimal] = Field(None, description="最小变动价位")
    trading_months: Optional[str] = Field(None, description="交易月份规则", max_length=50)
    delivery_months: Optional[str] = Field(None, description="交割月份规则", max_length=50)
    delivery_method: Optional[str] = Field(None, description="交割方式", max_length=20)
    last_trade_day_rule: Optional[str] = Field(None, description="最后交易日规则描述")
    is_active: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, description="品种描述")


class FuturesVarietyResponse(BaseModel):
    """期货品种响应."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    exchange: str
    market_id: Optional[UUID]
    contract_unit: Optional[Decimal]
    min_price_tick: Optional[Decimal]
    trading_months: Optional[str]
    delivery_months: Optional[str]
    delivery_method: Optional[str]
    last_trade_day_rule: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: date
    updated_at: date


class FuturesVarietyListItem(BaseModel):
    """期货品种列表项（简化版）."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    exchange: str
    is_active: bool