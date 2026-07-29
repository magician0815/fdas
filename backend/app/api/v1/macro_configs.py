"""
宏观数据源配置管理 API.

提供配置的 CRUD、启用/禁用定时调度.

Author: FDAS Team
Created: 2026-07-29
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.macro_config import (
    MacroConfigCreate,
    MacroConfigResponse,
    MacroConfigUpdate,
)
from app.services.macro_config_service import MacroConfigService
from app.services.macro_collection_service import macro_collection_service

router = APIRouter(prefix="/macro/configs", tags=["宏观数据源配置"])


@router.get("", response_model=dict)
async def list_configs(db: AsyncSession = Depends(get_db)):
    """获取所有宏观数据源配置列表."""
    service = MacroConfigService(db)
    configs = await service.list_configs()
    return {
        "success": True,
        "data": [MacroConfigResponse.model_validate(c).model_dump() for c in configs],
        "total": len(configs),
    }


@router.get("/{config_id}", response_model=dict)
async def get_config(config_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取单个配置详情."""
    service = MacroConfigService(db)
    config = await service.get_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return {"success": True, "data": MacroConfigResponse.model_validate(config).model_dump()}


@router.post("", response_model=dict, status_code=201)
async def create_config(data: MacroConfigCreate, db: AsyncSession = Depends(get_db)):
    """创建新配置."""
    service = MacroConfigService(db)
    try:
        config = await service.create_config(data.model_dump())
        return {"success": True, "data": MacroConfigResponse.model_validate(config).model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/{config_id}", response_model=dict)
async def update_config(config_id: UUID, data: MacroConfigUpdate, db: AsyncSession = Depends(get_db)):
    """更新配置(支持修改 URL、parse_config、调度表达式等)."""
    service = MacroConfigService(db)
    config = await service.update_config(config_id, data.model_dump(exclude_none=True))
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return {"success": True, "data": MacroConfigResponse.model_validate(config).model_dump()}


@router.delete("/{config_id}", response_model=dict)
async def delete_config(config_id: UUID, db: AsyncSession = Depends(get_db)):
    """删除配置(级联删除关联数据)."""
    # 先禁用调度
    await macro_collection_service.disable_schedule(config_id, db)

    service = MacroConfigService(db)
    deleted = await service.delete_config(config_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="配置不存在")
    return {"success": True, "message": "配置已删除"}


@router.post("/{config_id}/enable", response_model=dict)
async def enable_config(config_id: UUID, db: AsyncSession = Depends(get_db)):
    """启用定时调度."""
    success = await macro_collection_service.enable_schedule(config_id, db)
    if not success:
        raise HTTPException(status_code=400, detail="启用失败: 配置不存在或缺少 cron 表达式")
    return {"success": True, "message": "定时调度已启用"}


@router.post("/{config_id}/disable", response_model=dict)
async def disable_config(config_id: UUID, db: AsyncSession = Depends(get_db)):
    """禁用定时调度."""
    await macro_collection_service.disable_schedule(config_id, db)
    return {"success": True, "message": "定时调度已禁用"}
