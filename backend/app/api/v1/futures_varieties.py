"""
期货品种信息管理API.

提供期货品种的CRUD、列表查询等功能.

Author: FDAS Team
Created: 2026-04-23
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import logging

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.models.futures_variety import FuturesVariety
from app.models.datasource import DataSource
from app.schemas.futures_variety import (
    FuturesVarietyCreate,
    FuturesVarietyUpdate,
    FuturesVarietyResponse,
    FuturesVarietyListItem,
)
from app.schemas.common import Response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=Response)
async def list_futures_varieties(
    active_only: bool = Query(True, description="是否只返回启用的品种"),
    search: Optional[str] = Query(None, description="搜索代码或名称"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    获取期货品种列表.

    仅admin可访问.
    """
    query = select(FuturesVariety)

    if active_only:
        query = query.where(FuturesVariety.is_active == True)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (FuturesVariety.code.ilike(search_pattern)) |
            (FuturesVariety.name.ilike(search_pattern))
        )

    query = query.order_by(FuturesVariety.code)

    result = await db.execute(query)
    varieties = result.scalars().all()

    return Response(
        success=True,
        data=[FuturesVarietyListItem.model_validate(v) for v in varieties],
    )


@router.get("/{variety_id}", response_model=Response)
async def get_futures_variety(
    variety_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    获取期货品种详情.

    仅admin可访问.
    """
    result = await db.execute(
        select(FuturesVariety).where(FuturesVariety.id == variety_id)
    )
    variety = result.scalar_one_or_none()

    if not variety:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="期货品种不存在"
        )

    return Response(
        success=True,
        data=FuturesVarietyResponse.model_validate(variety),
    )


@router.post("/", response_model=Response)
async def create_futures_variety(
    request: FuturesVarietyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    创建期货品种.

    仅admin可访问.
    """
    result = await db.execute(
        select(FuturesVariety).where(FuturesVariety.code == request.code.upper())
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"期货品种代码 {request.code} 已存在"
        )

    if request.datasource_id:
        result = await db.execute(
            select(DataSource).where(DataSource.id == request.datasource_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数据源不存在"
            )

    variety = FuturesVariety(
        code=request.code.upper(),
        name=request.name,
        description=request.description,
        exchange=request.exchange,
        datasource_id=request.datasource_id,
        is_active=request.is_active,
    )
    db.add(variety)
    await db.commit()
    await db.refresh(variety)

    logger.info(f"创建期货品种: {variety.code} - {variety.name}")

    return Response(
        success=True,
        data=FuturesVarietyResponse.model_validate(variety),
        message="期货品种创建成功",
    )


@router.put("/{variety_id}", response_model=Response)
async def update_futures_variety(
    variety_id: UUID,
    request: FuturesVarietyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    更新期货品种.

    仅admin可访问.
    """
    result = await db.execute(
        select(FuturesVariety).where(FuturesVariety.id == variety_id)
    )
    variety = result.scalar_one_or_none()

    if not variety:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="期货品种不存在"
        )

    if request.datasource_id:
        result = await db.execute(
            select(DataSource).where(DataSource.id == request.datasource_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数据源不存在"
            )

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(variety, key, value)

    await db.commit()
    await db.refresh(variety)

    logger.info(f"更新期货品种: {variety.code}")

    return Response(
        success=True,
        data=FuturesVarietyResponse.model_validate(variety),
        message="期货品种更新成功",
    )


@router.delete("/{variety_id}", response_model=Response)
async def delete_futures_variety(
    variety_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    删除期货品种.

    仅admin可访问.
    """
    result = await db.execute(
        select(FuturesVariety).where(FuturesVariety.id == variety_id)
    )
    variety = result.scalar_one_or_none()

    if not variety:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="期货品种不存在"
        )

    await db.delete(variety)
    await db.commit()

    logger.info(f"删除期货品种: {variety.code}")

    return Response(
        success=True,
        message="期货品种删除成功",
    )