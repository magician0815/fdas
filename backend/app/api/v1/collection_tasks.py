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
        # 检查是否已存在同名任务
        result = await db.execute(
            select(CollectionTask).where(CollectionTask.name == request.name.strip())
        )
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

    # 4. 验证标的存在且属于该市场
    if market and market.code == "forex":
        result = await db.execute(
            select(ForexSymbol).where(ForexSymbol.id == request.symbol_id)
        )
        symbol = result.scalar_one_or_none()
        if not symbol:
            validation_result.errors.append("外汇标的不存在")
            validation_result.valid = False
        elif not symbol.is_active:
            validation_result.warnings.append("标的已停用")

        # 补充信息：标的名称
        if symbol:
            validation_result.info["symbol_name"] = symbol.name
            validation_result.info["symbol_code"] = symbol.code

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

    # 根据市场验证标的是否存在
    if market.code == "forex":
        result = await db.execute(
            select(ForexSymbol).where(ForexSymbol.id == request.symbol_id)
        )
        symbol = result.scalar_one_or_none()
        if not symbol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标的不存在"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"暂不支持市场类型: {market.name}"
        )

    # 验证日期范围
    if request.start_date and request.end_date:
        if request.start_date > request.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始日期不能晚于结束日期"
            )

    task = CollectionTask(**request.model_dump())
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

    # 目前只支持外汇市场
    if market.code != "forex":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"暂不支持手动执行市场类型: {market.name}"
        )

    # 创建执行日志
    log = CollectionTaskLog(
        task_id=task.id,
        run_at=datetime.now(timezone.utc),
        status="running",
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)

    start_time = datetime.now(timezone.utc)

    try:
        # 确定日期范围
        if request.force or not task.start_date:
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
        else:
            start_date = task.start_date
            end_date = task.end_date or date.today()

        # 检查是否有已有数据，从最新日期继续采集
        if not request.force:
            latest_date = await forex_daily_service.get_latest_date(db, task.symbol_id)
            if latest_date and latest_date < end_date:
                start_date = latest_date + timedelta(days=1)
                logger.info(f"从最新日期继续采集: {start_date}")

        # 执行采集
        records_count = await forex_daily_service.collect_and_save(
            db=db,
            symbol_id=task.symbol_id,
            datasource_id=task.datasource_id,
            start_date=start_date,
            end_date=end_date,
        )

        # 更新执行日志
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        log.status = "success"
        log.records_count = records_count
        log.duration_ms = duration_ms
        log.message = f"成功采集 {records_count} 条数据"

        # 更新任务状态
        task.last_run_at = datetime.now(timezone.utc)
        task.last_status = "success"
        task.last_message = log.message
        task.last_records_count = records_count

        await db.commit()
        await db.refresh(log)

        logger.info(f"任务执行成功: {task.name}, 采集 {records_count} 条数据")

        return Response(
            success=True,
            data=TaskExecuteResponse(
                task_id=task.id,
                task_name=task.name,
                symbol=str(task.symbol_id),
                status="success",
                records_count=records_count,
                message=log.message,
                duration_ms=duration_ms,
            ),
            message="任务执行成功",
        )

    except Exception as e:
        # 更新执行日志为失败
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        log.status = "failed"
        log.message = str(e)
        log.duration_ms = duration_ms

        # 更新任务状态
        task.last_run_at = datetime.now(timezone.utc)
        task.last_status = "failed"
        task.last_message = str(e)

        await db.commit()

        logger.error(f"任务执行失败: {task.name}, 错误: {str(e)}")

        return Response(
            success=False,
            message=f"任务执行失败: {str(e)}",
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