"""
采集任务管理API.

提供采集任务的CRUD、启停、手动执行、日志查询、参数校验等功能.

Author: FDAS Team
Created: 2026-04-10
Updated: 2026-04-11 - 新增参数预校验API
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, date, timedelta, timezone
import logging

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.models.collection_task import CollectionTask
from app.models.collection_task_log import CollectionTaskLog
from app.models.datasource import DataSource
from app.models.market import Market
from app.models.forex_symbol import ForexSymbol
from app.models.stock_symbol import StockSymbol
from app.models.bond_symbol import BondSymbol
from app.models.futures_contract import FuturesContract
from app.schemas.collection_task import (
    CollectionTaskCreate,
    CollectionTaskUpdate,
    CollectionTaskResponse,
    CollectionTaskLogResponse,
    CollectionTaskValidateRequest,
    ValidateResult,
    TaskExecuteRequest,
    TaskExecuteResponse,
)
from app.schemas.common import Response
from app.services.forex_daily_service import forex_daily_service
from app.services.stock_daily_service import stock_daily_service
from app.services.futures_daily_service import futures_daily_service
from app.services.bond_daily_service import bond_daily_service
from app.services.collection_service import collection_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/validate", response_model=Response)
async def validate_collection_params(
    request: CollectionTaskValidateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    参数预校验接口.

    在创建任务前验证参数有效性，返回详细的校验结果.
    仅admin可访问.
    """
    validation_result = ValidateResult()

    # 1. 验证任务名称
    if request.name:
        if len(request.name.strip()) < 2:
            validation_result.errors.append("任务名称至少需要2个字符")
            validation_result.valid = False
        # 检查是否已存在同名任务（编辑时排除自身）
        name_query = select(CollectionTask).where(CollectionTask.name == request.name.strip())
        if request.exclude_task_id:
            name_query = name_query.where(CollectionTask.id != request.exclude_task_id)
        result = await db.execute(name_query)
        if result.scalar_one_or_none():
            validation_result.warnings.append("已存在同名任务，建议修改名称")

    # 2. 验证数据源存在且属于该市场
    result = await db.execute(
        select(DataSource).where(DataSource.id == request.datasource_id)
    )
    datasource = result.scalar_one_or_none()
    if not datasource:
        validation_result.errors.append("数据源不存在")
        validation_result.valid = False
    elif not datasource.is_active:
        validation_result.warnings.append("数据源已停用，可能无法正常采集")

    # 3. 验证市场存在
    result = await db.execute(
        select(Market).where(Market.id == request.market_id)
    )
    market = result.scalar_one_or_none()
    if not market:
        validation_result.errors.append("市场不存在")
        validation_result.valid = False

    # 4. 验证标的存在（优先 symbol_id，回退 symbol_ids 首个）
    check_id = request.symbol_id or (request.symbol_ids[0] if request.symbol_ids else None)
    if check_id and market:
        if market.code == "forex":
            result = await db.execute(select(ForexSymbol).where(ForexSymbol.id == check_id))
            symbol = result.scalar_one_or_none()
            if not symbol:
                validation_result.errors.append("外汇标的不存在")
                validation_result.valid = False
            elif not symbol.is_active:
                validation_result.warnings.append("标的已停用")
            if symbol:
                validation_result.info["symbol_name"] = symbol.name
                validation_result.info["symbol_code"] = symbol.code
                if request.symbol_ids:
                    validation_result.info["symbol_count"] = len(request.symbol_ids)
        elif market.code in ["stock_cn", "stock_us", "stock_hk"]:
            result = await db.execute(select(StockSymbol).where(StockSymbol.id == check_id))
            symbol = result.scalar_one_or_none()
            if not symbol:
                validation_result.errors.append("股票标的不存在")
                validation_result.valid = False
            elif not symbol.is_active:
                validation_result.warnings.append("标的已停用")
            if symbol:
                validation_result.info["symbol_name"] = symbol.name
                validation_result.info["symbol_code"] = symbol.code
                validation_result.info["market"] = market.code
                if request.symbol_ids:
                    validation_result.info["symbol_count"] = len(request.symbol_ids)
        elif market.code in ["forex", "crypto"]:
            result = await db.execute(select(ForexSymbol).where(ForexSymbol.id == check_id))
            symbol = result.scalar_one_or_none()
            if not symbol:
                validation_result.errors.append("标的不存在")
                validation_result.valid = False
            if symbol:
                validation_result.info["symbol_name"] = symbol.name
                validation_result.info["symbol_code"] = symbol.code
        elif market.code.startswith("futures"):
            # 支持合约ID和品种ID
            result = await db.execute(select(FuturesContract).where(FuturesContract.id == check_id))
            contract = result.scalar_one_or_none()
            if not contract:
                # 回退到品种查询
                from app.models.futures_variety import FuturesVariety
                vr = await db.execute(select(FuturesVariety).where(FuturesVariety.id == check_id))
                variety = vr.scalar_one_or_none()
                if not variety:
                    validation_result.errors.append("期货合约或品种不存在")
                    validation_result.valid = False
                else:
                    validation_result.info["symbol_name"] = variety.name
                    validation_result.info["symbol_code"] = variety.code
                    validation_result.info["is_variety"] = True
            else:
                if not contract.is_active:
                    validation_result.warnings.append("合约已停用")
                validation_result.info["symbol_name"] = contract.contract_name
                validation_result.info["symbol_code"] = contract.contract_code
                if request.symbol_ids:
                    validation_result.info["symbol_count"] = len(request.symbol_ids)
        elif market.code in ["bond_cn", "bond_us"]:
            result = await db.execute(select(BondSymbol).where(BondSymbol.id == check_id))
            symbol = result.scalar_one_or_none()
            if not symbol:
                validation_result.errors.append("债券标的不存在")
                validation_result.valid = False
            elif not symbol.is_active:
                validation_result.warnings.append("标的已停用")
            if symbol:
                validation_result.info["symbol_name"] = symbol.name
                validation_result.info["symbol_code"] = symbol.code
                validation_result.info["market"] = market.code
                if request.symbol_ids:
                    validation_result.info["symbol_count"] = len(request.symbol_ids)

    # 5. 验证日期范围
    if request.start_date and request.end_date:
        if request.start_date > request.end_date:
            validation_result.errors.append("开始日期不能晚于结束日期")
            validation_result.valid = False

        # 检查是否早于数据源最小日期
        if datasource and datasource.min_date:
            if request.start_date < datasource.min_date:
                validation_result.warnings.append(
                    f"开始日期早于数据源最早日期{datasource.min_date}，可能无法获取完整数据"
                )

        # 计算预估采集天数
        days = (request.end_date - request.start_date).days + 1
        validation_result.info["estimated_days"] = days
        validation_result.info["estimated_records"] = f"预估采集 {days} 天数据"

    # 6. 验证cron表达式（如果有）
    if request.cron_expr:
        parts = request.cron_expr.split()
        if len(parts) != 5:
            validation_result.errors.append("Cron表达式格式错误，应为5部分")
            validation_result.valid = False
        else:
            validation_result.info["cron_desc"] = f"定时执行: {request.cron_expr}"

    return Response(
        success=True,
        data=validation_result,
    )


@router.get("/", response_model=Response)
async def list_collection_tasks(
    market_id: UUID = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    获取采集任务列表.

    仅admin可访问.

    Args:
        market_id: 可选，按市场过滤
    """
    query = select(CollectionTask).order_by(CollectionTask.created_at.desc())
    if market_id:
        query = query.where(CollectionTask.market_id == market_id)

    result = await db.execute(query)
    tasks = result.scalars().all()

    return Response(
        success=True,
        data=[CollectionTaskResponse.model_validate(t) for t in tasks],
    )


@router.get("/{task_id}", response_model=Response)
async def get_collection_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    获取采集任务详情.

    仅admin可访问.
    """
    result = await db.execute(
        select(CollectionTask).where(CollectionTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采集任务不存在"
        )

    return Response(
        success=True,
        data=CollectionTaskResponse.model_validate(task),
    )


@router.post("/", response_model=Response)
async def create_collection_task(
    request: CollectionTaskCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    创建采集任务.

    仅admin可访问.
    """
    # 检查数据源是否存在
    result = await db.execute(
        select(DataSource).where(DataSource.id == request.datasource_id)
    )
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="数据源不存在"
        )

    # 检查市场是否存在
    result = await db.execute(
        select(Market).where(Market.id == request.market_id)
    )
    market = result.scalar_one_or_none()

    if not market:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="市场不存在"
        )

    # 根据市场验证标的是否存在（支持多标的 symbol_ids 和单标的 symbol_id）
    symbol_id_list = request.symbol_ids or []
    if not symbol_id_list and request.symbol_id:
        symbol_id_list = [request.symbol_id]
    if not symbol_id_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须至少选择一个标的"
        )

    for sid in symbol_id_list:
        if market.code == "forex":
            result = await db.execute(select(ForexSymbol).where(ForexSymbol.id == sid))
            if not result.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"标的不存在: {sid}")
        elif market.code in ["stock_cn", "stock_us", "stock_hk"]:
            result = await db.execute(select(StockSymbol).where(StockSymbol.id == sid))
            if not result.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"股票标的不存在: {sid}")
        elif market.code.startswith("futures"):
            result = await db.execute(select(FuturesContract).where(FuturesContract.id == sid))
            if not result.scalar_one_or_none():
                # 回退到品种ID
                from app.models.futures_variety import FuturesVariety
                vr = await db.execute(select(FuturesVariety).where(FuturesVariety.id == sid))
                if not vr.scalar_one_or_none():
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"期货合约/品种不存在: {sid}")
        elif market.code in ["bond_cn", "bond_us"]:
            result = await db.execute(select(BondSymbol).where(BondSymbol.id == sid))
            if not result.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"债券标的不存在: {sid}")
        elif market.code in ["forex", "crypto"]:
            result = await db.execute(select(ForexSymbol).where(ForexSymbol.id == sid))
            if not result.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"标的不存在: {sid}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"暂不支持市场类型: {market.name}")

    # 验证日期范围
    if request.start_date and request.end_date:
        if request.start_date > request.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始日期不能晚于结束日期"
            )

    task_data = request.model_dump()
    if task_data.get("symbol_ids"):
        task_data["symbol_ids"] = [str(sid) for sid in task_data["symbol_ids"]]
    task = CollectionTask(**task_data)
    db.add(task)
    await db.commit()
    await db.refresh(task)

    logger.info(f"创建采集任务: {task.name}, 市场: {market.name}")

    return Response(
        success=True,
        data=CollectionTaskResponse.model_validate(task),
        message="采集任务创建成功",
    )


@router.put("/{task_id}", response_model=Response)
async def update_collection_task(
    task_id: UUID,
    request: CollectionTaskUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    更新采集任务.

    仅admin可访问.
    """
    result = await db.execute(
        select(CollectionTask).where(CollectionTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采集任务不存在"
        )

    # 更新字段
    update_data = request.model_dump(exclude_unset=True)
    if update_data.get("symbol_ids"):
        update_data["symbol_ids"] = [str(sid) for sid in update_data["symbol_ids"]]

    # 如果更新数据源ID，验证数据源存在
    if "datasource_id" in update_data:
        result = await db.execute(
            select(DataSource).where(DataSource.id == update_data["datasource_id"])
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数据源不存在"
            )

    # 如果更新市场ID，验证市场存在
    if "market_id" in update_data:
        result = await db.execute(
            select(Market).where(Market.id == update_data["market_id"])
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="市场不存在"
            )

    for key, value in update_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)

    logger.info(f"更新采集任务: {task.name}")

    return Response(
        success=True,
        data=CollectionTaskResponse.model_validate(task),
        message="采集任务更新成功",
    )


@router.delete("/{task_id}", response_model=Response)
async def delete_collection_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    删除采集任务.

    仅admin可访问.
    """
    result = await db.execute(
        select(CollectionTask).where(CollectionTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采集任务不存在"
        )

    await db.delete(task)
    await db.commit()

    logger.info(f"删除采集任务: {task.name}")

    return Response(
        success=True,
        message="采集任务删除成功",
    )


@router.put("/{task_id}/enable", response_model=Response)
async def enable_collection_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    启用采集任务.

    仅admin可访问.
    """
    result = await db.execute(
        select(CollectionTask).where(CollectionTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采集任务不存在"
        )

    if not task.cron_expr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务未配置cron表达式，无法启用"
        )

    # 使用collection_service启用任务
    success = await collection_service.enable_task(task_id, db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="启用任务失败"
        )

    await db.refresh(task)

    logger.info(f"启用采集任务: {task.name}")

    return Response(
        success=True,
        data=CollectionTaskResponse.model_validate(task),
        message="采集任务已启用",
    )


@router.put("/{task_id}/disable", response_model=Response)
async def disable_collection_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    禁用采集任务.

    仅admin可访问.
    """
    await collection_service.disable_task(task_id, db)

    result = await db.execute(
        select(CollectionTask).where(CollectionTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    logger.info(f"禁用采集任务: {task.name if task else task_id}")

    return Response(
        success=True,
        data=CollectionTaskResponse.model_validate(task) if task else None,
        message="采集任务已禁用",
    )


@router.post("/{task_id}/execute", response_model=Response)
async def execute_collection_task(
    task_id: UUID,
    request: TaskExecuteRequest = TaskExecuteRequest(),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    手动执行采集任务.

    仅admin可访问.
    """
    result = await db.execute(
        select(CollectionTask).where(CollectionTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采集任务不存在"
        )

    # 获取市场信息
    result = await db.execute(
        select(Market).where(Market.id == task.market_id)
    )
    market = result.scalar_one_or_none()

    if not market:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="市场不存在"
        )

    # 委托给 collection_service 统一执行（含重试/补偿/通知机制），同步等待完成
    try:
        await collection_service.execute_task(task_id)
    except Exception as e:
        logger.error(f"执行采集任务异常: {task_id}, {str(e)[:200]}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"执行采集任务时发生异常: {str(e)[:200]}"
        )

    # 重新查询任务获取最新状态
    await db.refresh(task)
    result = await db.execute(
        select(CollectionTaskLog).where(CollectionTaskLog.task_id == task.id).order_by(CollectionTaskLog.run_at.desc()).limit(1)
    )
    latest_log = result.scalar_one_or_none()

    return Response(
        success=task.last_status != "failed",
        data=TaskExecuteResponse(
            task_id=task.id,
            task_name=task.name,
            symbol=f"{task.last_records_count}条",
            status=task.last_status or "unknown",
            records_count=task.last_records_count or 0,
            message=task.last_message or "",
            duration_ms=latest_log.duration_ms if latest_log else 0,
            symbol_results=latest_log.symbol_results if latest_log else None,
            failed_symbols=latest_log.failed_symbols if latest_log else None,
        ),
        message=task.last_message or "执行完成",
    )


@router.get("/{task_id}/logs", response_model=Response)
async def get_task_logs(
    task_id: UUID,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    获取采集任务执行日志.

    仅admin可访问.
    """
    result = await db.execute(
        select(CollectionTaskLog)
        .where(CollectionTaskLog.task_id == task_id)
        .order_by(CollectionTaskLog.run_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()

    return Response(
        success=True,
        data=[CollectionTaskLogResponse.model_validate(log) for log in logs],
    )