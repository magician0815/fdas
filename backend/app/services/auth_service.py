"""
认证服务.

提供密码加密、验证和用户认证功能.

Author: FDAS Team
Created: 2026-04-03
"""

import bcrypt
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User


def hash_password(password: str) -> str:
    """
    密码加密.

    使用bcrypt算法加密密码.

    Args:
        password: 明文密码

    Returns:
        str: 加密后的密码hash
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    密码验证.

    Args:
        password: 明文密码
        password_hash: 密码hash

    Returns:
        bool: 密码是否正确
    """
    return bcrypt.checkpw(
        password.encode('utf-8'),
        password_hash.encode('utf-8')
    )


async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str,
) -> Optional[User]:
    """
    用户认证.

    Args:
        db: 数据库会话
        username: 用户名
        password: 密码

    Returns:
        Optional[User]: 认证成功返回用户对象，失败返回None
    """
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None

    return user