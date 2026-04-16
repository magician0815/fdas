"""
用户相关Schema.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-16 - 添加密码复杂度验证
"""

import re
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional


class UserCreate(BaseModel):
    """创建用户请求."""

    username: str
    password: str
    role: str = "user"

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名."""
        if not v or not v.strip():
            raise ValueError('用户名不能为空')
        if len(v.strip()) < 3:
            raise ValueError('用户名至少3个字符')
        if len(v.strip()) > 50:
            raise ValueError('用户名最多50个字符')
        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码复杂度."""
        if not v:
            raise ValueError('密码不能为空')
        if len(v) < 6:
            raise ValueError('密码至少6个字符')
        if len(v) > 72:
            raise ValueError('密码最多72个字符（bcrypt限制）')
        # 可选：强制密码复杂度（字母+数字）
        # if not re.search(r'[A-Za-z]', v) or not re.search(r'[0-9]', v):
        #     raise ValueError('密码必须包含字母和数字')
        return v


class UserUpdate(BaseModel):
    """更新用户请求."""

    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """验证用户名."""
        if v is not None:
            if not v.strip():
                raise ValueError('用户名不能为空')
            if len(v.strip()) < 3:
                raise ValueError('用户名至少3个字符')
            if len(v.strip()) > 50:
                raise ValueError('用户名最多50个字符')
            return v.strip()
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """验证密码复杂度."""
        if v is not None:
            if len(v) < 6:
                raise ValueError('密码至少6个字符')
            if len(v) > 72:
                raise ValueError('密码最多72个字符（bcrypt限制）')
        return v


class UserResponse(BaseModel):
    """用户响应."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    role: str