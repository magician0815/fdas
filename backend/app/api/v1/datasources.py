"""
数据源管理API.

提供数据源的CRUD、配置查看、货币对更新等功能.

Author: FDAS Team
Created: 2026-04-10
Updated: 2026-04-23 - 添加Market模型导入
"""

import json
from typing import List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import logging

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.models.datasource import DataSource
from app.models.market import Market
from app.schemas.datasource import (
    DataSourceCreate,
    DataSourceUpdate,
    DataSourceResponse,
    SupportedSymbolsResponse,
    SymbolInfo,
)
from app.schemas.common import Response
from app.collectors.akshare_collector import akshare_collector

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=Response)
async def list_datasources(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    获取数据源列表.

    仅admin可访问.
    """
    result = await db.execute(select(DataSource).order_by(DataSource.created_at))
    datasources = result.scalars().all()

    return Response(
        success=True,
        data=[DataSourceResponse.model_validate(ds) for ds in datasources],
    )


@router.get("/{datasource_id}", response_model=Response)
async def get_datasource(
    datasource_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    获取数据源详情.

    仅admin可访问.
    """
    result = await db.execute(
        select(DataSource).where(DataSource.id == datasource_id)
    )
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )

    return Response(
        success=True,
        data=DataSourceResponse.model_validate(datasource),
    )


@router.post("/", response_model=Response)
async def create_datasource(
    request: DataSourceCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    创建数据源.

    仅admin可访问.
    """
    # 检查名称是否已存在
    result = await db.execute(
        select(DataSource).where(DataSource.name == request.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="数据源名称已存在"
        )

    datasource = DataSource(**request.model_dump())
    db.add(datasource)
    await db.commit()
    await db.refresh(datasource)

    logger.info(f"创建数据源: {datasource.name}")

    return Response(
        success=True,
        data=DataSourceResponse.model_validate(datasource),
        message="数据源创建成功",
    )


@router.put("/{datasource_id}", response_model=Response)
async def update_datasource(
    datasource_id: UUID,
    request: DataSourceUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    更新数据源.

    仅admin可访问.
    """
    result = await db.execute(
        select(DataSource).where(DataSource.id == datasource_id)
    )
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )

    # 更新字段
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(datasource, key, value)

    await db.commit()
    await db.refresh(datasource)

    logger.info(f"更新数据源: {datasource.name}")

    return Response(
        success=True,
        data=DataSourceResponse.model_validate(datasource),
        message="数据源更新成功",
    )


@router.delete("/{datasource_id}", response_model=Response)
async def delete_datasource(
    datasource_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    删除数据源.

    仅admin可访问. 删除数据源会级联删除相关采集任务.
    """
    result = await db.execute(
        select(DataSource).where(DataSource.id == datasource_id)
    )
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )

    await db.delete(datasource)
    await db.commit()

    logger.info(f"删除数据源: {datasource.name}")

    return Response(
        success=True,
        message="数据源删除成功",
    )


@router.get("/{datasource_id}/symbols", response_model=Response)
async def get_supported_symbols(
    datasource_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    获取数据源支持的货币对列表.

    仅admin可访问.
    """
    result = await db.execute(
        select(DataSource).where(DataSource.id == datasource_id)
    )
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )

    # 获取货币对列表
    symbols = await akshare_collector.fetch_supported_symbols()

    return Response(
        success=True,
        data={
            "datasource_id": datasource_id,
            "datasource_name": datasource.name,
            "symbols": symbols,
        },
    )


@router.post("/{datasource_id}/symbols/fetch", response_model=Response)
async def fetch_and_compare_symbols(
    datasource_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    实时获取货币对并比较变更.

    获取最新的货币对列表，与数据库中存储的列表比较，
    返回新增和移除的货币对.

    仅admin可访问.
    """
    result = await db.execute(
        select(DataSource).where(DataSource.id == datasource_id)
    )
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )

    # 获取最新货币对列表
    fetched_symbols = await akshare_collector.fetch_supported_symbols()
    fetched_values = [s["value"] for s in fetched_symbols]

    # 当前存储的货币对列表
    current_symbols = datasource.supported_symbols or []

    # 计算变更
    added = [s for s in fetched_values if s not in current_symbols]
    removed = [s for s in current_symbols if s not in fetched_values]
    has_changes = len(added) > 0 or len(removed) > 0

    response_data = SupportedSymbolsResponse(
        datasource_id=datasource.id,
        datasource_name=datasource.name,
        current_symbols=current_symbols,
        fetched_symbols=[SymbolInfo(**s) for s in fetched_symbols],
        has_changes=has_changes,
        added=added,
        removed=removed,
    )

    return Response(
        success=True,
        data=response_data,
    )


@router.put("/{datasource_id}/symbols", response_model=Response)
async def update_supported_symbols(
    datasource_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    更新数据源支持的货币对列表.

    从AKShare实时获取最新货币对列表并更新到数据库.

    仅admin可访问.
    """
    result = await db.execute(
        select(DataSource).where(DataSource.id == datasource_id)
    )
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )

    # 获取最新货币对列表
    fetched_symbols = await akshare_collector.fetch_supported_symbols()
    symbol_values = [s["value"] for s in fetched_symbols]

    # 更新数据库
    datasource.supported_symbols = symbol_values
    await db.commit()
    await db.refresh(datasource)

    logger.info(f"更新数据源 {datasource.name} 支持的货币对: {len(symbol_values)}个")

    return Response(
        success=True,
        data=DataSourceResponse.model_validate(datasource),
        message=f"成功更新 {len(symbol_values)} 个货币对",
    )


@router.post("/{datasource_id}/sync-to-database", response_model=Response)
async def sync_symbols_to_database(
    datasource_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    从数据源同步金融标的到数据库.

    根据市场类型区分处理：
    - 外汇市场：调用AKShare获取货币对列表
    - A股市场：使用配置中的symbol_mapping
    仅admin可访问.
    """
    from app.models.forex_symbol import ForexSymbol

    result = await db.execute(
        select(DataSource).where(DataSource.id == datasource_id)
    )
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )

    # 获取市场信息判断类型
    market_code = None
    if datasource.market_id:
        market_result = await db.execute(
            select(Market).where(Market.id == datasource.market_id)
        )
        market = market_result.scalar_one_or_none()
        if market:
            market_code = market.code

    fetched_symbols = []
    symbol_names = []  # 用于更新supported_symbols字段

    if market_code and market_code.startswith("stock"):
        # 股票（A股/美股/港股）：通过采集器统一标的获取（含API+默认回退）
        config = json.loads(datasource.config_file) if datasource.config_file else {}
        try:
            stock_symbols = await akshare_collector.fetch_symbols_by_config(config)
            if stock_symbols:
                for s in stock_symbols:
                    code = s.get("code", "")
                    name = s.get("name", "")
                    if code and name:
                        fetched_symbols.append({"code": code, "value": name})
                        symbol_names.append(name)
                logger.info(f"通过采集器获取股票标的成功，共 {len(stock_symbols)} 个")
            else:
                logger.warning("采集器未返回股票标的")
        except Exception as e:
            logger.error(f"通过采集器获取股票标的失败: {str(e)}")

        # A股额外获取指数标的（上证指数、深证成指、沪深300等）
        if market_code == "stock_cn":
            try:
                import akshare as ak
                import asyncio
                df = await asyncio.to_thread(ak.stock_zh_index_spot_sina)
                for _, row in df.iterrows():
                    raw_code = str(row.get("代码", ""))
                    name = str(row.get("名称", ""))
                    # 指数代码带交易所前缀 (sh000001, sz399001)
                    if raw_code.startswith("sh") or raw_code.startswith("sz"):
                        code = raw_code  # keep prefix for indices
                    else:
                        code = raw_code
                    if code and name:
                        fetched_symbols.append({"code": code, "value": name})
                        symbol_names.append(name)
                logger.info(f"获取指数标的成功，新增 {len(df)} 个")
            except Exception as e:
                logger.warning(f"获取指数标的失败（非关键）: {e}")
    elif market_code and market_code.startswith("futures"):
        # 期货（国内/国际）：通过采集器统一标的获取
        config = json.loads(datasource.config_file) if datasource.config_file else {}
        try:
            fut_symbols = await akshare_collector.fetch_symbols_by_config(config)
            if fut_symbols:
                for s in fut_symbols:
                    code = s.get("code", "")
                    name = s.get("name", "")
                    if code and name:
                        fetched_symbols.append({"code": code, "value": name})
                        symbol_names.append(name)
                logger.info(f"通过采集器获取期货标的成功，共 {len(fut_symbols)} 个")
        except Exception as e:
            logger.warning(f"通过采集器获取期货标的失败: {e}")
    elif market_code and market_code.startswith("bond"):
        # 债券（国内债券/美债）：通过采集器统一标的获取
        config = json.loads(datasource.config_file) if datasource.config_file else {}
        try:
            bond_symbols = await akshare_collector.fetch_symbols_by_config(config)
            if bond_symbols:
                for s in bond_symbols:
                    code = s.get("code", "")
                    name = s.get("name", "")
                    if code and name:
                        fetched_symbols.append({"code": code, "value": name})
                        symbol_names.append(name)
                logger.info(f"通过采集器获取债券标的成功，共 {len(bond_symbols)} 个")
        except Exception as e:
            logger.warning(f"通过采集器获取债券标的失败: {e}")
    else:
        # 外汇：统一通过配置的 symbol_fetch 获取标的
        config = json.loads(datasource.config_file) if datasource.config_file else {}
        try:
            forex_symbols = await akshare_collector.fetch_symbols_by_config(config)
            if forex_symbols:
                for s in forex_symbols:
                    code = s.get("code", "")
                    name = s.get("name", s.get("value", ""))
                    if code and name:
                        fetched_symbols.append({"code": code, "value": name})
                        symbol_names.append(name)
                logger.info(f"通过采集器获取外汇标的成功，共 {len(forex_symbols)} 个")
        except Exception as e:
            logger.warning(f"通过采集器获取外汇标的失败: {e}")

    added_count = 0
    updated_count = 0
    skipped_count = 0

    for symbol_info in fetched_symbols:
        if market_code and market_code.startswith("stock"):
            # 股票（A股/美股/港股）：使用StockSymbol模型
            from app.models.stock_symbol import StockSymbol
            market_name = "A股" if market_code == "stock_cn" else ("美股" if market_code == "stock_us" else "港股")
            result = await db.execute(
                select(StockSymbol).where(
                    StockSymbol.code == symbol_info["code"],
                    StockSymbol.market_id == datasource.market_id,
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                if existing.name != symbol_info["value"]:
                    existing.name = symbol_info["value"]
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                new_symbol = StockSymbol(
                    code=symbol_info["code"],
                    name=symbol_info["value"],
                    market_id=datasource.market_id,
                    datasource_id=datasource_id,
                    is_active=True,
                )
                db.add(new_symbol)
                added_count += 1
        elif market_code and market_code.startswith("bond"):
            # 债券：使用BondSymbol模型
            from app.models.bond_symbol import BondSymbol
            result = await db.execute(
                select(BondSymbol).where(
                    BondSymbol.code == symbol_info["code"],
                    BondSymbol.market_id == datasource.market_id,
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                if existing.name != symbol_info["value"]:
                    existing.name = symbol_info["value"]
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                new_symbol = BondSymbol(
                    code=symbol_info["code"],
                    name=symbol_info["value"],
                    market_id=datasource.market_id,
                    datasource_id=datasource_id,
                    bond_type="国债" if market_code == "bond_us" else "企业债",
                    is_active=True,
                )
                db.add(new_symbol)
                added_count += 1
        elif market_code and market_code.startswith("futures"):
            # 期货（国内/国际）：使用FuturesVariety模型
            from app.models.futures_variety import FuturesVariety as FV
            result = await db.execute(
                select(FV).where(
                    FV.code == symbol_info["code"],
                    FV.market_id == datasource.market_id,
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                if existing.name != symbol_info["value"]:
                    existing.name = symbol_info["value"]
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                new_symbol = FV(
                    code=symbol_info["code"],
                    name=symbol_info["value"],
                    exchange="global",
                    market_id=datasource.market_id,
                    is_active=True,
                )
                db.add(new_symbol)
                added_count += 1
        else:
            # 外汇：使用ForexSymbol模型
            result = await db.execute(
                select(ForexSymbol).where(
                    ForexSymbol.code == symbol_info["code"],
                    ForexSymbol.market_id == datasource.market_id,
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                if existing.name != symbol_info["value"]:
                    existing.name = symbol_info["value"]
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                new_symbol = ForexSymbol(
                    code=symbol_info["code"],
                    name=symbol_info["value"],
                    market_id=datasource.market_id,
                    datasource_id=datasource_id,
                    base_currency=symbol_info["code"][:3] if len(symbol_info["code"]) >= 3 else "",
                    quote_currency=symbol_info["code"][3:] if len(symbol_info["code"]) >= 3 else "",
                    is_active=True,
                )
                db.add(new_symbol)
                added_count += 1

    # 更新数据源的supported_symbols字段
    datasource.supported_symbols = symbol_names
    await db.commit()

    logger.info(f"同步金融标的到数据库: 新增{added_count}, 更新{updated_count}, 跳过{skipped_count}")

    return Response(
        success=True,
        data={
            "added": added_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "total": len(fetched_symbols),
        },
        message=f"同步完成：新增 {added_count} 个，更新 {updated_count} 个",
    )


# ==================== 配置管理API ====================

class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    config_file: str = Field(..., min_length=1, description="配置文件JSON字符串")


@router.get("/{datasource_id}/config", response_model=Response)
async def get_datasource_config(
    datasource_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    获取数据源配置文件.

    仅admin可访问.
    """
    result = await db.execute(
        select(DataSource).where(DataSource.id == datasource_id)
    )
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )

    return Response(
        success=True,
        data={
            "datasource_id": str(datasource_id),
            "datasource_name": datasource.name,
            "config_file": datasource.config_file or "",
            "config_version": datasource.config_version,
            "config_updated_at": datasource.config_updated_at.isoformat() if datasource.config_updated_at else None,
        },
    )


@router.put("/{datasource_id}/config", response_model=Response)
async def update_datasource_config(
    datasource_id: UUID,
    request: ConfigUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    更新数据源配置文件.

    仅admin可访问.
    """
    from app.services.datasource_config_service import get_datasource_config_service
    from app.schemas.datasource_config_schema import get_default_forex_config

    config_json = request.config_file

    # 如果没有提供配置，使用默认配置
    if not config_json.strip():
        config_json = get_default_forex_config()

    result = await db.execute(
        select(DataSource).where(DataSource.id == datasource_id)
    )
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )

    # 保存配置
    config_service = get_datasource_config_service(db)
    success, error_msg = await config_service.save_config(datasource_id, config_json)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    logger.info(f"更新数据源配置: {datasource.name}")

    return Response(
        success=True,
        message="配置更新成功",
    )


@router.get("/{datasource_id}/export", response_model=Response)
async def export_datasource_config(
    datasource_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    导出数据源配置文件.

    仅admin可访问.
    """
    from app.services.datasource_config_service import get_datasource_config_service

    result = await db.execute(
        select(DataSource).where(DataSource.id == datasource_id)
    )
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )

    config_service = get_datasource_config_service(db)
    config_json = await config_service.export_config(datasource_id)

    return Response(
        success=True,
        data={
            "datasource_id": str(datasource_id),
            "datasource_name": datasource.name,
            "config_file": config_json or "",
        },
    )


class ImportConfigRequest(BaseModel):
    """导入配置请求"""
    config_file: str = Field(..., min_length=1, description="配置文件JSON字符串")
    name: str = Field(..., min_length=1, max_length=100, description="数据源名称")
    market_id: UUID = Field(..., description="市场ID")


@router.post("/import", response_model=Response)
async def import_datasource_config(
    request: ImportConfigRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    导入数据源配置文件创建新数据源.

    仅admin可访问.
    """
    from app.services.datasource_config_service import get_datasource_config_service

    config_file = request.config_file
    name = request.name
    market_id = request.market_id

    if not config_file.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="配置文件不能为空"
        )

    if not name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="数据源名称不能为空"
        )

    if not market_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="市场ID不能为空"
        )

    config_service = get_datasource_config_service(db)
    success, error_msg, datasource_id = await config_service.import_config(
        config_file, name, market_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    logger.info(f"导入数据源配置: {name}")

    return Response(
        success=True,
        data={"datasource_id": str(datasource_id)},
        message="数据源导入成功",
    )