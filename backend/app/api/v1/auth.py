"""
认证API路由.

Author: FDAS Team
Created: 2026-04-03
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import LoginRequest, UserResponse
from app.schemas.common import Response
from app.services.auth_service import authenticate_user
from app.services.session_service import SessionService

router = APIRouter()


@router.post("/login", response_model=Response)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    用户登录.

    Args:
        request: 登录请求
        db: 数据库会话

    Returns:
        Response: 登录结果
    """
    # 验证用户
    user = await authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 创建Session
    session_service = SessionService()
    session = await session_service.create_session(
        db=db,
        user_id=user.id,
        expires_hours=24,
    )

    return Response(
        success=True,
        data={
            "user": UserResponse(
                id=str(user.id),
                username=user.username,
                role=user.role,
            ),
            "session_id": str(session.id),
        },
        message="登录成功",
    )


@router.post("/logout", response_model=Response)
async def logout(
    db: AsyncSession = Depends(get_db),
):
    """
    用户登出.

    TODO: 实现Session清除

    Returns:
        Response: 登出结果
    """
    return Response(
        success=True,
        message="登出成功",
    )