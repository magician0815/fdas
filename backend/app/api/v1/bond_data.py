"""
债券行情数据API.

提供债券日线行情数据的查询功能，支持周期切换（日线/周线/月线）.

Author: FDAS Team
Created: 2026-04-23
Updated: 2026-04-29 - 新增周期切换功能（daily/weekly/monthly）
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date as DateType, date as date_cls, timedelta

from app.core.database import get_db
from app.models.user import User
from app.services.bond_daily_service import bond_daily_service
from app.services.period_aggregation_service import PeriodAggregationService, PeriodType
from app.schemas.bond_daily import BondDailyListItem
from app.schemas.common import Response

router = APIRouter(prefix="/bond/data", tags=["债券行情数据"])


@router.get("/", response_model=Response)
async def get_bond_daily_data(
    symbol_id: Optional[UUID] = Query(None, description="债券ID"),
    market_id: Optional[UUID] = Query(None, description="市场ID"),
    start_date: Optional[DateType] = Query(None, description="开始日期"),
    end_date: Optional[DateType] = Query(None, description="结束日期"),
    period: str = Query("daily", description="周期类型（daily/weekly/monthly）"),
    limit: int = Query(1000, ge=1, le=5000, description="返回数据条数限制"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取债券行情数据（支持日线/周线/月线）.

    Args:
        symbol_id: 债券ID（可选）
        market_id: 市场ID（可选，用于区分国内/国际债券）
        start_date: 开始日期
        end_date: 结束日期
        period: 周期类型（daily/weekly/monthly）
        limit: 数据条数限制

    Returns:
        债券行情数据列表
    """
    # 默认时间范围根据周期调整
    if not start_date:
        if period == "daily":
            start_date = date_cls.today() - timedelta(days=1460)
        elif period == "weekly":
            start_date = date_cls.today() - timedelta(days=2080)
        elif period == "monthly":
            start_date = date_cls.today() - timedelta(days=1920)
        else:
            start_date = date_cls.today() - timedelta(days=1460)

    if not end_date:
        end_date = date_cls.today()

    # 获取日线数据（升序，用于聚合计算）
    raw_data = await bond_daily_service.get_bond_daily_asc(
        db=db,
        symbol_id=symbol_id,
        market_id=market_id,
        start_date=start_date,
        end_date=end_date,
        limit=5000,
    )

    if not raw_data:
        return Response(
            success=True,
            data=[],
        )

    # 转换为字典列表
    daily_items = [BondDailyListItem.model_validate(d).model_dump() for d in raw_data]

    # 根据周期类型聚合数据
    if period == PeriodType.DAILY:
        result_data = daily_items
    elif period in (PeriodType.WEEKLY, PeriodType.MONTHLY):
        aggregation_service = PeriodAggregationService()
        result_data = aggregation_service.aggregate(daily_items, period)
    else:
        result_data = daily_items

    # 限制返回条数
    result_data = result_data[-limit:] if len(result_data) > limit else result_data

    return Response(
        success=True,
        data=result_data,
        message=f"返回 {len(result_data)} 条数据 (period={period})",
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
