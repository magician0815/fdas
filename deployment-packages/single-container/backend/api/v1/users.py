"""
用户管理API路由.

Author: FDAS Team
Created: 2026-04-03
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import Response
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=Response)
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    获取用户列表.

    仅admin可访问.
    """
    service = UserService()
    users = await service.get_users(db)
    return Response(
        success=True,
        data=[UserResponse.model_validate(u) for u in users],
    )


@router.post("/", response_model=Response)
async def create_user(
    request: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    创建用户.

    仅admin可访问.
    """
    service = UserService()
    user = await service.create_user(
        db=db,
        username=request.username,
        password=request.password,
        role=request.role,
    )
    return Response(
        success=True,
        data=UserResponse.model_validate(user),
        message="用户创建成功",
    )


@router.put("/{user_id}", response_model=Response)
async def update_user(
    user_id: str,
    request: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    更新用户.

    仅admin可访问.
    """
    from uuid import UUID
    service = UserService()
    user = await service.update_user(
        db=db,
        user_id=UUID(user_id),
        **request.model_dump(exclude_unset=True),
    )
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return Response(
        success=True,
        data=UserResponse.model_validate(user),
        message="用户更新成功",
    )


@router.delete("/{user_id}", response_model=Response)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    删除用户.

    仅admin可访问.
    """
    from uuid import UUID
    service = UserService()
    success = await service.delete_user(db, UUID(user_id))
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return Response(success=True, message="用户删除成功")