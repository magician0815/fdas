"""
期货行情数据API.

提供期货日线行情数据的查询功能.

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
from app.services.futures_daily_service import futures_daily_service
from app.schemas.futures_daily import FuturesDailyListItem, FuturesDailyQuery
from app.schemas.common import Response

router = APIRouter(prefix="/futures/data", tags=["期货行情数据"])


@router.get("/", response_model=Response)
async def get_futures_daily_data(
    contract_id: Optional[UUID] = Query(None, description="合约ID"),
    variety_id: Optional[UUID] = Query(None, description="品种ID"),
    start_date: Optional[DateType] = Query(None, description="开始日期"),
    end_date: Optional[DateType] = Query(None, description="结束日期"),
    is_main_data: Optional[bool] = Query(None, description="是否仅查询主力合��"),
    limit: int = Query(1000, ge=1, le=5000, description="返回数据条数限制"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取期货日线行情数据（按日期降序）.

    Args:
        contract_id: 合约ID（可选）
        variety_id: 品种ID（可选）
        start_date: 开始日期
        end_date: 结束日期
        is_main_data: 是否仅查询主力合约数据
        limit: 数据条数限制

    Returns:
        期货日线数据列表
    """
    data = await futures_daily_service.get_futures_daily(
        db=db,
        contract_id=contract_id,
        variety_id=variety_id,
        start_date=start_date,
        end_date=end_date,
        is_main_data=is_main_data,
        limit=limit,
    )

    return Response(
        success=True,
        data=[FuturesDailyListItem.model_validate(d) for d in data],
        message=f"返回 {len(data)} 条数据",
    )


@router.get("/{contract_id}/latest", response_model=Response)
async def get_futures_latest_data(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定合约的最新数据.

    Args:
        contract_id: 合约ID

    Returns:
        最新一条日线数据
    """
    data = await futures_daily_service.get_futures_daily(
        db=db,
        contract_id=contract_id,
        limit=1,
    )

    if not data:
        return Response(
            success=False,
            message="暂无数据",
        )

    return Response(
        success=True,
        data=FuturesDailyListItem.model_validate(data[0]),
    )


@router.get("/{contract_id}/latest-date", response_model=Response)
async def get_futures_latest_date(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定合约的最新数据日期.

    Args:
        contract_id: 合约ID

    Returns:
        最新日期
    """
    latest_date = await futures_daily_service.get_latest_date(db, contract_id)

    if not latest_date:
        return Response(
            success=False,
            message="暂无数据",
        )

    return Response(
        success=True,
        data={"contract_id": str(contract_id), "latest_date": latest_date},
    )