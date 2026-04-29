"""
债券标的Schema.

定义债券标的基础信息相关的请求和响应模型.

Author: FDAS Team
Created: 2026-04-23
"""

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from decimal import Decimal


class BondSymbolBase(BaseModel):
    """债券标的基础模型."""
    code: str = Field(..., description="债券代码", max_length=20)
    name: str = Field(..., description="债券名称", max_length=100)
    bond_type: str = Field(..., description="债券类型（国债/企业债/可转债/金融债）", max_length=20)
    issuer: Optional[str] = Field(None, description="发行人", max_length=100)
    is_active: bool = Field(default=True, description="是否启用")
    description: Optional[str] = Field(None, description="债券描述")


class BondSymbolCreate(BondSymbolBase):
    """创建债券标的请求."""
    market_id: Optional[UUID] = Field(None, description="所属市场ID")
    datasource_id: Optional[UUID] = Field(None, description="默认数据来源ID")
    coupon_rate: Optional[Decimal] = Field(None, description="票面利率（百分比）")
    maturity_date: Optional[date] = Field(None, description="到期日期")
    face_value: Optional[Decimal] = Field(default=100.00, description="面值")
    currency: Optional[str] = Field(default="CNY", description="币种", max_length=10)
    rating: Optional[str] = Field(None, description="信用评级", max_length=10)


class BondSymbolUpdate(BaseModel):
    """更新债券标的请求."""
    name: Optional[str] = Field(None, description="债券名称", max_length=100)
    market_id: Optional[UUID] = Field(None, description="所属市场ID")
    bond_type: Optional[str] = Field(None, description="债券类型", max_length=20)
    issuer: Optional[str] = Field(None, description="发行人", max_length=100)
    datasource_id: Optional[UUID] = Field(None, description="默认数据来源ID")
    coupon_rate: Optional[Decimal] = Field(None, description="票面利率（百分比）")
    maturity_date: Optional[date] = Field(None, description="到期日期")
    face_value: Optional[Decimal] = Field(None, description="面值")
    currency: Optional[str] = Field(None, description="币种", max_length=10)
    rating: Optional[str] = Field(None, description="信用评级", max_length=10)
    is_active: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, description="债券描述")


class BondSymbolResponse(BaseModel):
    """债券标的响应."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    market_id: Optional[UUID]
    bond_type: str
    issuer: Optional[UUID]
    coupon_rate: Optional[Decimal]
    maturity_date: Optional[date]
    face_value: Optional[Decimal]
    currency: Optional[str]
    rating: Optional[str]
    datasource_id: Optional[UUID]
    is_active: bool
    description: Optional[str]
    created_at: date
    updated_at: date


class BondSymbolListItem(BaseModel):
    """债券标的列表项（简化版）."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    market_id: Optional[UUID]
    bond_type: str
    issuer: Optional[str]
    is_active: bool