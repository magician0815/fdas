"""
权限依赖注入.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-10 - 添加require_login依赖函数
"""

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.models.session import Session


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    获取当前登录用户.

    通过请求头或Cookie中的session_id验证用户身份.

    Raises:
        HTTPException: 401未授权
    """
    # 从请求头获取session_id
    session_id = request.headers.get("X-Session-ID")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
        )

    # 验证session有效性
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.is_valid == True)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="会话已过期或无效",
        )

    # 获取用户
    result = await db.execute(
        select(User).where(User.id == session.user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    return user


async def require_login(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    要求用户已登录.

    Args:
        current_user: 当前用户

    Returns:
        User: 已登录用户
    """
    return current_user


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