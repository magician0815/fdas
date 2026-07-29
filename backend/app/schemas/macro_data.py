"""
宏观数据点 Pydantic Schema.

Author: FDAS Team
Created: 2026-07-29
"""

from typing import Optional
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field


class MacroDataPointResponse(BaseModel):
    """宏观数据点响应."""
    id: UUID
    config_id: UUID
    source_code: str
    country: Optional[str]
    series_name: str
    indicator_key: str
    value: Optional[float]
    publish_date: date
    period_date: Optional[date]
    frequency: Optional[str]
    forecast_year: Optional[int]
    unit: Optional[str]
    extra_info: Optional[dict]
    created_at: datetime

    model_config = {"from_attributes": True}


class MacroDataQueryParams(BaseModel):
    """宏观数据查询参数."""
    source_code: Optional[str] = Field(None, description="数据源代码过滤")
    indicator_key: Optional[str] = Field(None, description="指标键名过滤")
    country: Optional[str] = Field(None, description="国家过滤")
    start_date: Optional[date] = Field(None, description="发布日期起始")
    end_date: Optional[date] = Field(None, description="发布日期截止")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=50, ge=1, le=200, description="每页条数")


class MacroDataListResponse(BaseModel):
    """宏观数据列表响应."""
    success: bool = True
    data: list[MacroDataPointResponse]
    meta: dict = Field(default_factory=lambda: {"total": 0, "page": 1, "page_size": 50})


class MacroDataLatestResponse(BaseModel):
    """最新数据响应."""
    success: bool = True
    data: Optional[MacroDataPointResponse] = None
