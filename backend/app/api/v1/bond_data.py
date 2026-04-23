"""
债券行情数据API.

提供债券日线行情数据的查询功能.

Author: FDAS Team
Created: 2026-04-23
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date as DateType

from app.core.database import get_db
from app.models.user import User
from app.services.bond_daily_service import bond_daily_service
from app.schemas.bond_daily import BondDailyListItem
from app.schemas.common import Response

router = APIRouter(prefix="/bond/data", tags=["债券行情数据"])


@router.get("/", response_model=Response)
async def get_bond_daily_data(
    symbol_id: Optional[UUID] = Query(None, description="债券ID"),
    market_id: Optional[UUID] = Query(None, description="市场ID"),
    start_date: Optional[DateType] = Query(None, description="开始日期"),
    end_date: Optional[DateType] = Query(None, description="结束日期"),
    limit: int = Query(1000, ge=1, le=5000, description="返回数据条数限制"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取债券日线行情数据（按日期降序）.

    Args:
        symbol_id: 债券ID（可选）
        market_id: 市场ID（可选，用于区分国内/国际债券）
        start_date: 开始日期
        end_date: 结束日期
        limit: 数据条数限制

    Returns:
        债券日线数据列表
    """
    data = await bond_daily_service.get_bond_daily(
        db=db,
        symbol_id=symbol_id,
        market_id=market_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    return Response(
        success=True,
        data=[BondDailyListItem.model_validate(d) for d in data],
        message=f"返回 {len(data)} 条数据",
    )


@router.get("/{symbol_id}/latest", response_model=Response)
async def get_bond_latest_data(
    symbol_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定债券的最新数据.

    Args:
        symbol_id: 债券ID

    Returns:
        最新一条日线数据
    """
    data = await bond_daily_service.get_bond_daily(
        db=db,
        symbol_id=symbol_id,
        limit=1,
    )

    if not data:
        return Response(
            success=False,
            message="暂无数据",
        )

    return Response(
        success=True,
        data=BondDailyListItem.model_validate(data[0]),
    )


@router.get("/{symbol_id}/latest-date", response_model=Response)
async def get_bond_latest_date(
    symbol_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定债券的最新数据日期.

    Args:
        symbol_id: 债券ID

    Returns:
        最新日期
    """
    latest_date = await bond_daily_service.get_latest_date(db, symbol_id)

    if not latest_date:
        return Response(
            success=False,
            message="暂无数据",
        )

    return Response(
        success=True,
        data={"symbol_id": str(symbol_id), "latest_date": latest_date},
    )