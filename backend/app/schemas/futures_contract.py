"""
期货合约Schema.

定义期货合约信息相关的请求和响应模型.

Author: FDAS Team
Created: 2026-04-23
"""

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from decimal import Decimal


class FuturesContractBase(BaseModel):
    """期货合约基础模型."""
    contract_code: str = Field(..., description="合约代码（如IF2401）", max_length=20)
    contract_name: str = Field(..., description="合约名称", max_length=100)
    contract_month: str = Field(..., description="合约月份标识", max_length=10)
    year: str = Field(..., description="合约年份", max_length=4)
    month: str = Field(..., description="合约月份（01-12）", max_length=2)
    is_active: bool = Field(default=True, description="是否启用")


class FuturesContractCreate(FuturesContractBase):
    """创建期货合约请求."""
    variety_id: UUID = Field(..., description="关联品种ID")
    listing_date: Optional[date] = Field(None, description="上市日期")
    last_trade_date: date = Field(..., description="最后交易日/到期日")
    delivery_date: Optional[date] = Field(None, description="交割日")
    is_main_contract: Optional[bool] = Field(default=False, description="是否为当前主力合约")
    datasource_id: Optional[UUID] = Field(None, description="数据来源ID")


class FuturesContractUpdate(BaseModel):
    """更新期货合约请求."""
    contract_name: Optional[str] = Field(None, description="合约名称", max_length=100)
    listing_date: Optional[date] = Field(None, description="上市日期")
    last_trade_date: Optional[date] = Field(None, description="最后交易日/到期日")
    delivery_date: Optional[date] = Field(None, description="交割日")
    is_main_contract: Optional[bool] = Field(None, description="是否为当前主力合约")
    main_start_date: Optional[date] = Field(None, description="成为主力合约的开始日期")
    main_end_date: Optional[date] = Field(None, description="作为主力合约的结束日期")
    open_interest: Optional[int] = Field(None, description="当前持仓量")
    datasource_id: Optional[UUID] = Field(None, description="数据来源ID")
    is_active: Optional[bool] = Field(None, description="是否启用")


class FuturesContractResponse(BaseModel):
    """期货合约响应."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    variety_id: UUID
    contract_code: str
    contract_name: str
    contract_month: str
    year: str
    month: str
    listing_date: Optional[date]
    last_trade_date: date
    delivery_date: Optional[date]
    is_main_contract: bool
    main_start_date: Optional[date]
    main_end_date: Optional[date]
    open_interest: Optional[int]
    datasource_id: Optional[UUID]
    is_active: bool
    created_at: date
    updated_at: date


class FuturesContractListItem(BaseModel):
    """期货合约列表项（简化版）."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    variety_id: UUID
    contract_code: str
    contract_name: str
    contract_month: str
    is_main_contract: bool
    last_trade_date: date
    is_active: bool