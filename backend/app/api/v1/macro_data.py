"""
宏观数据查询 API.

提供数据的分页查询、最新数据获取、按条件过滤.

Author: FDAS Team
Created: 2026-07-29
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional
from uuid import UUID

from app.core.database import get_db

router = APIRouter(prefix="/macro/data", tags=["宏观数据"])


@router.get("", response_model=dict)
async def query_data(
    source_code: Optional[str] = Query(None, description="数据源代码"),
    indicator_key: Optional[str] = Query(None, description="指标键名"),
    country: Optional[str] = Query(None, description="国家/地区"),
    start_date: Optional[date] = Query(None, description="发布日期起始(已废弃,请用period_start)"),
    end_date: Optional[date] = Query(None, description="发布日期截止(已废弃,请用period_end)"),
    period_start: Optional[date] = Query(None, description="数据期间起始"),
    period_end: Optional[date] = Query(None, description="数据期间截止"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=50, ge=1, le=200, description="每页条数"),
    db: AsyncSession = Depends(get_db),
):
    """分页查询宏观数据点(原始SQL避免分区表Identity Map问题)."""
    where_parts = []
    params = {}
    if source_code:
        where_parts.append("source_code = :sc")
        params["sc"] = source_code
    if indicator_key:
        where_parts.append("indicator_key = :ik")
        params["ik"] = indicator_key
    if country:
        where_parts.append("country = :ct")
        params["ct"] = country
    if period_start:
        where_parts.append("period_date >= :ps")
        params["ps"] = period_start
    if period_end:
        where_parts.append("period_date <= :pe")
        params["pe"] = period_end

    where = " AND ".join(where_parts) if where_parts else "1=1"
    params["lim"] = page_size
    params["off"] = (page - 1) * page_size

    # 总数
    count_sql = f"SELECT COUNT(*) FROM macro_data_points WHERE {where}"
    total_result = await db.execute(text(count_sql), params)
    total = total_result.scalar() or 0

    # 数据
    data_sql = f"SELECT * FROM macro_data_points WHERE {where} ORDER BY period_date DESC LIMIT :lim OFFSET :off"
    result = await db.execute(text(data_sql), params)
    rows = result.fetchall()

    data = [{
        "id": str(r[0]), "config_id": str(r[1]), "source_code": r[2], "country": r[3],
        "series_name": r[4], "indicator_key": r[5], "value": float(r[6]) if r[6] else None,
        "publish_date": str(r[7]) if r[7] else None, "period_date": str(r[8]) if r[8] else None,
        "frequency": r[9], "forecast_year": r[10], "unit": r[11],
        "extra_info": r[12] or {}, "created_at": str(r[14]) if len(r) > 14 else None,
    } for r in rows]

    return {
        "success": True,
        "data": data,
        "meta": {"total": total, "page": page, "page_size": page_size},
    }


@router.get("/{source_code}/latest", response_model=dict)
async def get_latest(source_code: str, db: AsyncSession = Depends(get_db)):
    """获取指定数据源的最新数据."""
    result = await db.execute(
        text("SELECT * FROM macro_data_points WHERE source_code = :sc ORDER BY period_date DESC LIMIT 1"),
        {"sc": source_code}
    )
    r = result.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail=f"未找到 {source_code} 的数据")
    return {"success": True, "data": {
        "id": str(r[0]), "config_id": str(r[1]), "source_code": r[2], "country": r[3],
        "series_name": r[4], "indicator_key": r[5], "value": float(r[6]) if r[6] else None,
        "publish_date": str(r[7]) if r[7] else None, "period_date": str(r[8]) if r[8] else None,
        "frequency": r[9], "forecast_year": r[10], "unit": r[11],
        "extra_info": r[12] or {}, "created_at": str(r[14]) if len(r) > 14 else None,
    }}
