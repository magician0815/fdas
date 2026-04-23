"""
股票日线行情Schema.

定义股票日线行情数据的响应模型.

Author: FDAS Team
Created: 2026-04-23
"""

from typing import Optional, List
from datetime import date as DateType
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from decimal import Decimal


class StockDailyBase(BaseModel):
    """股票日线行情基础模型."""
    symbol_id: UUID = Field(..., description="关联股票ID")
    market_id: UUID = Field(..., description="所属市场ID")
    datasource_id: Optional[UUID] = Field(None, description="数据来源ID")
    date: DateType = Field(..., description="交易日期")


class StockDailyResponse(BaseModel):
    """股票日线行情响应."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    symbol_id: UUID
    market_id: UUID
    datasource_id: Optional[UUID]
    date: DateType
    open: Optional[Decimal]
    high: Optional[Decimal]
    low: Optional[Decimal]
    close: Optional[Decimal]
    volume: Optional[int]
    amount: Optional[Decimal]
    turnover: Optional[Decimal]
    change_pct: Optional[Decimal]
    change_amount: Optional[Decimal]
    amplitude: Optional[Decimal]
    is_suspended: bool
    is_st: bool
    updated_at: DateType


class StockDailyListItem(BaseModel):
    """股票日线行情列表项（简化版）."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    symbol_id: UUID
    market_id: UUID
    date: DateType
    open: Optional[Decimal]
    high: Optional[Decimal]
    low: Optional[Decimal]
    close: Optional[Decimal]
    volume: Optional[int]
    change_pct: Optional[Decimal]


class StockDailyQuery(BaseModel):
    """股票日线行情查询请求."""
    symbol_id: Optional[UUID] = Field(None, description="股票ID（可选，不传则查所有）")
    market_id: Optional[UUID] = Field(None, description="市场ID（用于区分A股/美股/港股）")
    start_date: Optional[DateType] = Field(None, description="开始日期")
    end_date: Optional[DateType] = Field(None, description="结束日期")
    limit: int = Field(default=1000, description="返回数据条数限制", ge=1, le=5000)