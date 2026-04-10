"""
外汇标的基础信息管理API.

提供外汇标的的CRUD、列表查询等功能.

Author: FDAS Team
Created: 2026-04-10
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import logging

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.models.forex_symbol import ForexSymbol
from app.models.datasource import DataSource
from app.schemas.forex_symbol import (
    ForexSymbolCreate,
    ForexSymbolUpdate,
    ForexSymbolResponse,
    ForexSymbolListItem,
)
from app.schemas.common import Response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=Response)
async def list_forex_symbols(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    获取外汇标的列表.

    仅admin可访问.

    Args:
        active_only: 是否只返回启用的标的，默认True
    """
    query = select(ForexSymbol)
    if active_only:
        query = query.where(ForexSymbol.is_active == True)
    query = query.order_by(ForexSymbol.code)

    result = await db.execute(query)
    symbols = result.scalars().all()

    return Response(
        success=True,
        data=[ForexSymbolListItem.model_validate(s) for s in symbols],
    )


@router.get("/{symbol_id}", response_model=Response)
async def get_forex_symbol(
    symbol_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    获取外汇标的详情.

    仅admin可访问.
    """
    result = await db.execute(
        select(ForexSymbol).where(ForexSymbol.id == symbol_id)
    )
    symbol = result.scalar_one_or_none()

    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="外汇标的不存在"
        )

    return Response(
        success=True,
        data=ForexSymbolResponse.model_validate(symbol),
    )


@router.get("/code/{code}", response_model=Response)
async def get_forex_symbol_by_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    根据代码获取外汇标的.

    仅admin可访问.
    """
    result = await db.execute(
        select(ForexSymbol).where(ForexSymbol.code == code.upper())
    )
    symbol = result.scalar_one_or_none()

    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"货币对代码 {code} 不存在"
        )

    return Response(
        success=True,
        data=ForexSymbolResponse.model_validate(symbol),
    )


@router.post("/", response_model=Response)
async def create_forex_symbol(
    request: ForexSymbolCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    创建外汇标的.

    仅admin可访问.
    """
    # 检查代码是否已存在
    result = await db.execute(
        select(ForexSymbol).where(ForexSymbol.code == request.code.upper())
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"货币对代码 {request.code} 已存在"
        )

    # 验证数据源是否存在（如果指定）
    if request.datasource_id:
        result = await db.execute(
            select(DataSource).where(DataSource.id == request.datasource_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数据源不存在"
            )

    symbol = ForexSymbol(
        code=request.code.upper(),
        name=request.name,
        description=request.description,
        datasource_id=request.datasource_id,
        base_currency=request.base_currency,
        quote_currency=request.quote_currency,
        is_active=request.is_active,
        first_trade_date=request.first_trade_date,
    )
    db.add(symbol)
    await db.commit()
    await db.refresh(symbol)

    logger.info(f"创建外汇标的: {symbol.code} - {symbol.name}")

    return Response(
        success=True,
        data=ForexSymbolResponse.model_validate(symbol),
        message="外汇标的创建成功",
    )


@router.put("/{symbol_id}", response_model=Response)
async def update_forex_symbol(
    symbol_id: UUID,
    request: ForexSymbolUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    更新外汇标的.

    仅admin可访问.
    """
    result = await db.execute(
        select(ForexSymbol).where(ForexSymbol.id == symbol_id)
    )
    symbol = result.scalar_one_or_none()

    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="外汇标的不存在"
        )

    # 验证数据源是否存在（如果指定）
    if request.datasource_id:
        result = await db.execute(
            select(DataSource).where(DataSource.id == request.datasource_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数据源不存在"
            )

    # 更新字段
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(symbol, key, value)

    await db.commit()
    await db.refresh(symbol)

    logger.info(f"更新外汇标的: {symbol.code}")

    return Response(
        success=True,
        data=ForexSymbolResponse.model_validate(symbol),
        message="外汇标的更新成功",
    )


@router.delete("/{symbol_id}", response_model=Response)
async def delete_forex_symbol(
    symbol_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    删除外汇标的.

    仅admin可访问. 删除标的前会检查是否有关联的采集任务.
    """
    result = await db.execute(
        select(ForexSymbol).where(ForexSymbol.id == symbol_id)
    )
    symbol = result.scalar_one_or_none()

    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="外汇标的不存在"
        )

    # 检查是否有关联的采集任务
    from app.models.collection_task import CollectionTask
    result = await db.execute(
        select(CollectionTask).where(CollectionTask.symbol_id == symbol_id).limit(1)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该标的有关联的采集任务，无法删除"
        )

    await db.delete(symbol)
    await db.commit()

    logger.info(f"删除外汇标的: {symbol.code}")

    return Response(
        success=True,
        message="外汇标的删除成功",
    )