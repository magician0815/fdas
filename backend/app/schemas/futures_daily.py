"""
期货日线行情Schema.

定义期货日线行情数据的响应模型.

Author: FDAS Team
Created: 2026-04-23
"""

from typing import Optional
from datetime import date as DateType
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from decimal import Decimal


class FuturesDailyBase(BaseModel):
    """期货日线行情基础模型."""
    contract_id: UUID = Field(..., description="关联合约ID")
    variety_id: UUID = Field(..., description="关联品种ID")
    datasource_id: Optional[UUID] = Field(None, description="数据来源ID")
    date: DateType = Field(..., description="交易日期")


class FuturesDailyResponse(BaseModel):
    """期货日线行情响应."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    contract_id: UUID
    variety_id: UUID
    datasource_id: Optional[UUID]
    date: DateType
    open: Optional[Decimal]
    high: Optional[Decimal]
    low: Optional[Decimal]
    close: Optional[Decimal]
    settle_price: Optional[Decimal]
    volume: Optional[int]
    open_interest: Optional[int]
    turnover: Optional[Decimal]
    change_pct: Optional[Decimal]
    change_amount: Optional[Decimal]
    amplitude: Optional[Decimal]
    oi_change: Optional[int]
    is_main_data: bool
    adjusted_price: Optional[Decimal]
    updated_at: DateType


class FuturesDailyListItem(BaseModel):
    """期货日线行情列表项（简化版）."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    contract_id: UUID
    variety_id: UUID
    date: DateType
    open: Optional[Decimal]
    high: Optional[Decimal]
    low: Optional[Decimal]
    close: Optional[Decimal]
    settle_price: Optional[Decimal]
    volume: Optional[int]
    open_interest: Optional[int]
    change_pct: Optional[Decimal]


class FuturesDailyQuery(BaseModel):
    """期货日线行情查询请求."""
    variety_id: Optional[UUID] = Field(None, description="品种ID（可选，不传则查所有）")
    contract_id: Optional[UUID] = Field(None, description="合约ID（可选）")
    start_date: Optional[DateType] = Field(None, description="开始日期")
    end_date: Optional[DateType] = Field(None, description="结束日期")
    is_main_data: Optional[bool] = Field(None, description="是否仅查询主力合约数据")
    limit: int = Field(default=1000, description="返回数据条数限制", ge=1, le=5000)