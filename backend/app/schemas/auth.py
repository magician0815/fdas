"""
认证相关Schema.

Author: FDAS Team
Created: 2026-04-03
"""

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    """登录请求."""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    role: str