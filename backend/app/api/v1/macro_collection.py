"""
宏观数据采集触发/日志 API.

提供手动触发采集和日志查询功能.

Author: FDAS Team
Created: 2026-07-29
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.models.macro_log import MacroCollectionLog
from app.schemas.macro_log import MacroLogResponse
from app.services.macro_collection_service import macro_collection_service

router = APIRouter(prefix="/macro", tags=["宏观采集"])


@router.post("/configs/{config_id}/collect", response_model=dict)
async def trigger_collect(config_id: UUID, full: bool = Query(default=False, description="是否全量采集")):
    """手动触发采集任务(异步执行)."""
    message = await macro_collection_service.trigger_collect(config_id, full=full)
    return {"success": True, "message": message}


@router.get("/logs", response_model=dict)
async def query_logs(
    config_id: Optional[UUID] = Query(None, description="配置ID过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
):
    """分页查询采集日志."""
    conditions = []
    if config_id:
        conditions.append(MacroCollectionLog.config_id == config_id)
    if status:
        conditions.append(MacroCollectionLog.status == status)

    base = select(MacroCollectionLog).where(*conditions)

    count_query = select(func.count()).select_from(base.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    data_query = base.order_by(desc(MacroCollectionLog.run_at)).offset(offset).limit(page_size)
    result = await db.execute(data_query)
    rows = result.scalars().all()

    return {
        "success": True,
        "data": [MacroLogResponse.model_validate(r).model_dump() for r in rows],
        "meta": {"total": total, "page": page, "page_size": page_size},
    }
