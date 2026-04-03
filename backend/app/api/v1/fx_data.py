"""
汇率数据API路由.

Author: FDAS Team
Created: 2026-04-03
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from typing import Optional

from app.core.database import get_db
from app.schemas.common import Response
from app.services.fx_data_service import fx_data_service

router = APIRouter()


@router.get("/data", response_model=Response)
async def get_fx_data(
    symbol: str = Query(default="USDCNH", description="汇率符号"),
    start_date: Optional[date] = Query(default=None, description="开始日期"),
    end_date: Optional[date] = Query(default=None, description="结束日期"),
    limit: int = Query(default=1000, le=1000, description="数据条数限制"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取汇率数据.

    返回指定时间范围内的汇率数据，最多1000条.
    """
    # 默认查询最近30天
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    data = await fx_data_service.get_fx_data(
        db=db,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    return Response(
        success=True,
        data=[
            {
                "id": str(d.id),
                "symbol": d.symbol,
                "date": str(d.date),
                "open": float(d.open) if d.open else None,
                "high": float(d.high) if d.high else None,
                "low": float(d.low) if d.low else None,
                "close": float(d.close) if d.close else None,
                "volume": d.volume,
            }
            for d in data
        ],
    )