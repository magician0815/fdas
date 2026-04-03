"""
权限依赖注入.

Author: FDAS Team
Created: 2026-04-03
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User


async def get_current_user(
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    获取当前登录用户.

    TODO: 实现Session验证

    Raises:
        HTTPException: 401未授权
    """
    # 暂时抛出401，待实现Session验证
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="未登录",
    )


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    要求admin权限.

    Args:
        current_user: 当前用户

    Returns:
        User: admin用户

    Raises:
        HTTPException: 403权限不足
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user