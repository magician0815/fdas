"""
债券标的基础信息管理API.

提供债券标的的CRUD、列表查询等功能，支持国内/国际债券.

Author: FDAS Team
Created: 2026-04-23
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from uuid import UUID
import logging

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.models.bond_symbol import BondSymbol
from app.models.market import Market
from app.models.datasource import DataSource
from app.schemas.bond_symbol import (
    BondSymbolCreate,
    BondSymbolUpdate,
    BondSymbolResponse,
    BondSymbolListItem,
)
from app.schemas.common import Response
from app.services.market_registry import market_registry

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=Response)
async def list_bond_symbols(
    market_id: Optional[UUID] = Query(None, description="市场ID过滤"),
    active_only: bool = Query(True, description="是否只返回启用的标的"),
    search: Optional[str] = Query(None, description="搜索代码或名称"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    获取债券标的列表.

    仅admin可访问.
    """
    query = select(BondSymbol)

    if market_id:
        query = query.where(BondSymbol.market_id == market_id)

    if active_only:
        query = query.where(BondSymbol.is_active == True)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                BondSymbol.code.ilike(search_pattern),
                BondSymbol.name.ilike(search_pattern)
            )
        )

    query = query.order_by(BondSymbol.code)

    result = await db.execute(query)
    symbols = result.scalars().all()

    return Response(
        success=True,
        data=[BondSymbolListItem.model_validate(s) for s in symbols],
    )


@router.get("/{symbol_id}", response_model=Response)
async def get_bond_symbol(
    symbol_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    获取债券标的详情.

    仅admin可访问.
    """
    result = await db.execute(
        select(BondSymbol).where(BondSymbol.id == symbol_id)
    )
    symbol = result.scalar_one_or_none()

    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="债券标的不存在"
        )

    return Response(
        success=True,
        data=BondSymbolResponse.model_validate(symbol),
    )


@router.get("/code/{code}", response_model=Response)
async def get_bond_symbol_by_code(
    code: str,
    market_id: Optional[UUID] = Query(None, description="市场ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    根据代码获取债券标的.

    仅admin可访问.
    """
    query = select(BondSymbol).where(BondSymbol.code == code.upper())
    if market_id:
        query = query.where(BondSymbol.market_id == market_id)

    result = await db.execute(query)
    symbol = result.scalar_one_or_none()

    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"债券代码 {code} 不存在"
        )

    return Response(
        success=True,
        data=BondSymbolResponse.model_validate(symbol),
    )


@router.post("/", response_model=Response)
async def create_bond_symbol(
    request: BondSymbolCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    创建债券标的.

    仅admin可访问.
    """
    result = await db.execute(
        select(Market).where(Market.id == request.market_id)
    )
    market = result.scalar_one_or_none()
    if not market:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="市场不存在"
        )

    if not market_registry.is_supported(market.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的市场类型: {market.name}"
        )

    result = await db.execute(
        select(BondSymbol).where(
            BondSymbol.code == request.code.upper(),
            BondSymbol.market_id == request.market_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"债券代码 {request.code} 在该市场中已存在"
        )

    if request.datasource_id:
        result = await db.execute(
            select(DataSource).where(DataSource.id == request.datasource_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数据源不存在"
            )

    symbol = BondSymbol(
        code=request.code.upper(),
        name=request.name,
        description=request.description,
        market_id=request.market_id,
        datasource_id=request.datasource_id,
        bond_type=request.bond_type,
        coupon_rate=request.coupon_rate,
        maturity_date=request.maturity_date,
        is_active=request.is_active,
    )
    db.add(symbol)
    await db.commit()
    await db.refresh(symbol)

    logger.info(f"创建债券标的: {symbol.code} - {symbol.name}, 市场: {market.code}")

    return Response(
        success=True,
        data=BondSymbolResponse.model_validate(symbol),
        message="债券标的创建成功",
    )


@router.put("/{symbol_id}", response_model=Response)
async def update_bond_symbol(
    symbol_id: UUID,
    request: BondSymbolUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    更新债券标的.

    仅admin可访问.
    """
    result = await db.execute(
        select(BondSymbol).where(BondSymbol.id == symbol_id)
    )
    symbol = result.scalar_one_or_none()

    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="债券标的不存在"
        )

    if request.market_id:
        result = await db.execute(
            select(Market).where(Market.id == request.market_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="市场不存在"
            )

    if request.datasource_id:
        result = await db.execute(
            select(DataSource).where(DataSource.id == request.datasource_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数据源不存在"
            )

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(symbol, key, value)

    await db.commit()
    await db.refresh(symbol)

    logger.info(f"更新债券标的: {symbol.code}")

    return Response(
        success=True,
        data=BondSymbolResponse.model_validate(symbol),
        message="债券标的更新成功",
    )


@router.delete("/{symbol_id}", response_model=Response)
async def delete_bond_symbol(
    symbol_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    删除债券标的.

    仅admin可访问.
    """
    result = await db.execute(
        select(BondSymbol).where(BondSymbol.id == symbol_id)
    )
    symbol = result.scalar_one_or_none()

    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="债券标的不存在"
        )

    await db.delete(symbol)
    await db.commit()

    logger.info(f"删除债券标的: {symbol.code}")

    return Response(
        success=True,
        message="债券标的删除成功",
    )