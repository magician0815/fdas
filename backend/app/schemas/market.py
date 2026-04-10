"""
市场类型Schema.

定义市场类型相关的请求和响应模型.

Author: FDAS Team
Created: 2026-04-10
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class MarketBase(BaseModel):
    """市场类型基础模型."""
    code: str = Field(..., description="市场代码", max_length=20)
    name: str = Field(..., description="市场名称", max_length=50)
    description: Optional[str] = Field(None, description="市场描述")
    timezone: str = Field(default="Asia/Shanghai", description="市场时区", max_length=50)
    is_active: bool = Field(default=True, description="是否启用")


class MarketCreate(MarketBase):
    """创建市场类型请求."""
    pass


class MarketUpdate(BaseModel):
    """更新市场类型请求."""
    name: Optional[str] = Field(None, description="市场名称", max_length=50)
    description: Optional[str] = Field(None, description="市场描述")
    timezone: Optional[str] = Field(None, description="市场时区", max_length=50)
    is_active: Optional[bool] = Field(None, description="是否启用")


class MarketResponse(BaseModel):
    """市场类型响应."""
    id: UUID
    code: str
    name: str
    description: Optional[str]
    timezone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True