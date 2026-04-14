"""
外汇日线数据API.

提供外汇日线行情数据查询和技术指标计算功能.
支持周期切换（日线/周线/月线）.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-14 - 新增周期切换功能（daily/weekly/monthly）
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.core.deps import require_login
from app.models.user import User
from app.schemas.common import Response
from app.services.forex_daily_service import forex_daily_service
from app.services.technical_service import technical_service
from app.services.period_aggregation_service import PeriodAggregationService, PeriodType

router = APIRouter()


class ForexDailyItem:
    """日线数据响应项."""
    def __init__(self, data):
        self.id = str(data.id)
        self.symbol_id = str(data.symbol_id)
        self.date = str(data.date)
        self.open = float(data.open) if data.open else None
        self.high = float(data.high) if data.high else None
        self.low = float(data.low) if data.low else None
        self.close = float(data.close) if data.close else None
        self.change_pct = float(data.change_pct) if data.change_pct else None
        self.change_amount = float(data.change_amount) if data.change_amount else None
        self.amplitude = float(data.amplitude) if data.amplitude else None

    def to_dict(self):
        return {
            "id": self.id,
            "symbol_id": self.symbol_id,
            "date": self.date,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "change_pct": self.change_pct,
            "change_amount": self.change_amount,
            "amplitude": self.amplitude,
        }


@router.get("/data", response_model=Response)
async def get_fx_data(
    symbol_id: Optional[UUID] = Query(default=None, description="货币对ID"),
    symbol_code: str = Query(default="USDCNY", description="货币对代码"),
    start_date: Optional[date] = Query(default=None, description="开始日期"),
    end_date: Optional[date] = Query(default=None, description="结束日期"),
    period: str = Query(default="daily", description="周期类型（daily/weekly/monthly）"),
    limit: int = Query(default=1000, le=1000, description="数据条数限制"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login),
):
    """
    获取外汇行情数据.

    返回指定时间范围内的行情数据，最多1000条.
    支持通过symbol_id或symbol_code查询.
    支持周期切换：daily（日线）/ weekly（周线）/ monthly（月线）
    """
    # 默认查询时间范围根据周期调整
    if not start_date:
        if period == "daily":
            start_date = date.today() - timedelta(days=30)
        elif period == "weekly":
            start_date = date.today() - timedelta(days=180)  # 约26周
        elif period == "monthly":
            start_date = date.today() - timedelta(days=365)  # 约12月
        else:
            start_date = date.today() - timedelta(days=30)

    if not end_date:
        end_date = date.today()

    # 获取日线数据（升序，用于聚合计算）
    raw_data = await forex_daily_service.get_forex_daily_asc(
        db=db,
        symbol_id=symbol_id,
        symbol_code=symbol_code,
        start_date=start_date,
        end_date=end_date,
        limit=500,  # 获取足够数据用于聚合
    )

    if not raw_data:
        return Response(
            success=True,
            data=[],
        )

    # 转换为字典列表
    daily_items = [ForexDailyItem(d).to_dict() for d in raw_data]

    # 根据周期类型聚合数据
    if period == PeriodType.DAILY:
        result_data = daily_items
    elif period == PeriodType.WEEKLY or period == PeriodType.MONTHLY:
        aggregation_service = PeriodAggregationService()
        result_data = aggregation_service.aggregate(daily_items, period)
    else:
        result_data = daily_items

    # 限制返回条数
    result_data = result_data[-limit:] if len(result_data) > limit else result_data

    return Response(
        success=True,
        data=result_data,
        meta={"period": period, "total": len(result_data)}
    )


@router.get("/data/{symbol_id}", response_model=Response)
async def get_fx_data_by_id(
    symbol_id: UUID,
    start_date: Optional[date] = Query(default=None, description="开始日期"),
    end_date: Optional[date] = Query(default=None, description="结束日期"),
    limit: int = Query(default=1000, le=1000, description="数据条数限制"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login),
):
    """
    根据标的ID获取外汇日线数据.

    返回指定时间范围内的日线数据.
    """
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    data = await forex_daily_service.get_forex_daily(
        db=db,
        symbol_id=symbol_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    return Response(
        success=True,
        data=[ForexDailyItem(d).to_dict() for d in data],
    )


@router.get("/indicators", response_model=Response)
async def get_indicators(
    symbol_id: Optional[UUID] = Query(default=None, description="货币对ID"),
    symbol_code: str = Query(default="USDCNY", description="货币对代码"),
    start_date: Optional[date] = Query(default=None, description="开始日期"),
    end_date: Optional[date] = Query(default=None, description="结束日期"),
    period: str = Query(default="daily", description="周期类型（daily/weekly/monthly）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login),
):
    """
    获取技术指标.

    返回MA、MACD等技术指标数据.
    支持通过symbol_id或symbol_code查询.
    支持周期切换：daily（日线）/ weekly（周线）/ monthly（月线）
    """
    # 默认查询时间范围根据周期调整（技术指标需要足够数据）
    if not start_date:
        if period == "daily":
            start_date = date.today() - timedelta(days=100)
        elif period == "weekly":
            start_date = date.today() - timedelta(days=365)  # 约52周
        elif period == "monthly":
            start_date = date.today() - timedelta(days=730)  # 约24月
        else:
            start_date = date.today() - timedelta(days=100)

    if not end_date:
        end_date = date.today()

    # 获取日线数据（升序）
    raw_data = await forex_daily_service.get_forex_daily_asc(
        db=db,
        symbol_id=symbol_id,
        symbol_code=symbol_code,
        start_date=start_date,
        end_date=end_date,
        limit=200,  # 获取足够数据用于聚合和指标计算
    )

    if not raw_data:
        return Response(
            success=True,
            data={"ma": {}, "macd": {"dif": [], "dea": [], "macd": []}, "vol": {}},
        )

    # 转换为字典列表
    daily_items = [ForexDailyItem(d).to_dict() for d in raw_data]

    # 根据周期聚合并计算指标
    aggregation_service = PeriodAggregationService()
    result = aggregation_service.aggregate_with_indicators(
        daily_items,
        period,
        ma_periods=[5, 10, 20, 60],
        macd_params={"fast": 12, "slow": 26, "signal": 9}
    )

    # 重新组织响应格式
    return Response(
        success=True,
        data={
            "data": result["data"],
            "ma": result["ma"],
            "macd": result["macd"],
        },
        meta={"period": period}
    )