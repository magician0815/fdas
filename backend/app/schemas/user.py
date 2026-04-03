"""
用户相关Schema.

Author: FDAS Team
Created: 2026-04-03
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserCreate(BaseModel):
    """创建用户请求."""
    username: str
    password: str
    role: str = "user"


class UserUpdate(BaseModel):
    """更新用户请求."""
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    """用户响应."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    role: str