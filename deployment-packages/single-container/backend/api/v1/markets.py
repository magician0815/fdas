"""
市场类型管理API.

提供市场类型的查询功能.

Author: FDAS Team
Created: 2026-04-10
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.models.market import Market
from app.schemas.market import MarketResponse
from app.schemas.common import Response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=Response)
async def list_markets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    获取市场类型列表.

    仅admin可访问.
    """
    result = await db.execute(
        select(Market).where(Market.is_active == True).order_by(Market.code)
    )
    markets = result.scalars().all()

    return Response(
        success=True,
        data=[MarketResponse.model_validate(m) for m in markets],
    )


@router.get("/all", response_model=Response)
async def list_all_markets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    获取所有市场类型（包括禁用的）.

    仅admin可访问.
    """
    result = await db.execute(select(Market).order_by(Market.code))
    markets = result.scalars().all()

    return Response(
        success=True,
        data=[MarketResponse.model_validate(m) for m in markets],
    )


@router.get("/{market_id}", response_model=Response)
async def get_market(
    market_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    获取市场类型详情.

    仅admin可访问.
    """
    from uuid import UUID

    try:
        market_uuid = UUID(market_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的市场ID格式"
        )

    result = await db.execute(
        select(Market).where(Market.id == market_uuid)
    )
    market = result.scalar_one_or_none()

    if not market:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="市场类型不存在"
        )

    return Response(
        success=True,
        data=MarketResponse.model_validate(market),
    )


@router.get("/code/{code}", response_model=Response)
async def get_market_by_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    根据代码获取市场类型.

    仅admin可访问.
    """
    result = await db.execute(
        select(Market).where(Market.code == code)
    )
    market = result.scalar_one_or_none()

    if not market:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"市场代码 {code} 不存在"
        )

    return Response(
        success=True,
        data=MarketResponse.model_validate(market),
    )