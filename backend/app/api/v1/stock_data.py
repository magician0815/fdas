"""
股票行情数据API.

提供股票日线行情数据的查询功能.

Author: FDAS Team
Created: 2026-04-23
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date as DateType

from app.core.database import get_db
from app.models.user import User
from app.services.stock_daily_service import stock_daily_service
from app.schemas.stock_daily import StockDailyResponse, StockDailyListItem
from app.schemas.common import Response

router = APIRouter(prefix="/stock/data", tags=["股票行情数据"])


@router.get("/", response_model=Response)
async def get_stock_daily_data(
    symbol_id: Optional[UUID] = Query(None, description="股票ID"),
    market_id: Optional[UUID] = Query(None, description="市场ID"),
    start_date: Optional[DateType] = Query(None, description="开始日期"),
    end_date: Optional[DateType] = Query(None, description="结束日期"),
    limit: int = Query(1000, ge=1, le=5000, description="返回数据条数限制"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取股票日线行情数据（按日期降序）.

    Args:
        symbol_id: 股票ID（可选）
        market_id: 市场ID（可选，用于区分A股/美股/港股）
        start_date: 开始日期
        end_date: 结束日期
        limit: 数据条数限制

    Returns:
        股票日线数据列表
    """
    data = await stock_daily_service.get_stock_daily(
        db=db,
        symbol_id=symbol_id,
        market_id=market_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    return Response(
        success=True,
        data=[StockDailyListItem.model_validate(d) for d in data],
        message=f"返回 {len(data)} 条数据",
    )


@router.get("/{symbol_id}/latest", response_model=Response)
async def get_stock_latest_data(
    symbol_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定股票的最新数据.

    Args:
        symbol_id: 股票ID

    Returns:
        最新一条日线数据
    """
    data = await stock_daily_service.get_stock_daily(
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
        data=StockDailyResponse.model_validate(data[0]),
    )


@router.get("/{symbol_id}/latest-date", response_model=Response)
async def get_stock_latest_date(
    symbol_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定股票的最新数据日期.

    Args:
        symbol_id: 股票ID

    Returns:
        最新日期
    """
    latest_date = await stock_daily_service.get_latest_date(db, symbol_id)

    if not latest_date:
        return Response(
            success=False,
            message="暂无数据",
        )

    return Response(
        success=True,
        data={"symbol_id": str(symbol_id), "latest_date": latest_date},
    )