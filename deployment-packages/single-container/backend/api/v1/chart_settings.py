"""
用户图表设置API.

提供用户图表个性化配置的存取功能.

Author: FDAS Team
Created: 2026-04-14
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.core.deps import require_login
from app.models.user import User
from app.models.user_chart_setting import UserChartSetting
from app.schemas.common import Response

router = APIRouter()


@router.get("/settings", response_model=Response)
async def get_chart_settings(
    setting_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login),
):
    """
    获取用户图表设置.

    返回指定类型的所有设置，或所有设置.
    """
    query = select(UserChartSetting).where(UserChartSetting.user_id == current_user.id)

    if setting_type:
        query = query.where(UserChartSetting.setting_type == setting_type)

    result = await db.execute(query)
    settings = result.scalars().all()

    return Response(
        success=True,
        data=[{
            "id": str(s.id),
            "type": s.setting_type,
            "key": s.setting_key,
            "value": s.setting_value,
            "updated_at": str(s.updated_at)
        } for s in settings]
    )


@router.get("/settings/{setting_type}/{setting_key}", response_model=Response)
async def get_chart_setting(
    setting_type: str,
    setting_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login),
):
    """
    获取单个图表设置.
    """
    result = await db.execute(
        select(UserChartSetting).where(
            UserChartSetting.user_id == current_user.id,
            UserChartSetting.setting_type == setting_type,
            UserChartSetting.setting_key == setting_key
        )
    )
    setting = result.scalar_one_or_none()

    if not setting:
        return Response(
            success=True,
            data=None
        )

    return Response(
        success=True,
        data={
            "id": str(setting.id),
            "type": setting.setting_type,
            "key": setting.setting_key,
            "value": setting.setting_value,
            "updated_at": str(setting.updated_at)
        }
    )


@router.post("/settings", response_model=Response)
async def save_chart_setting(
    setting_type: str,
    setting_key: str,
    setting_value: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login),
):
    """
    保存图表设置.

    创建或更新用户图表设置.
    """
    # 查找现有设置
    result = await db.execute(
        select(UserChartSetting).where(
            UserChartSetting.user_id == current_user.id,
            UserChartSetting.setting_type == setting_type,
            UserChartSetting.setting_key == setting_key
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # 更新现有设置
        existing.setting_value = setting_value
        await db.commit()
        await db.refresh(existing)
        return Response(
            success=True,
            data={
                "id": str(existing.id),
                "type": existing.setting_type,
                "key": existing.setting_key,
                "value": existing.setting_value,
                "updated_at": str(existing.updated_at)
            },
            message="设置已更新"
        )
    else:
        # 创建新设置
        new_setting = UserChartSetting(
            user_id=current_user.id,
            setting_type=setting_type,
            setting_key=setting_key,
            setting_value=setting_value
        )
        db.add(new_setting)
        await db.commit()
        await db.refresh(new_setting)
        return Response(
            success=True,
            data={
                "id": str(new_setting.id),
                "type": new_setting.setting_type,
                "key": new_setting.setting_key,
                "value": new_setting.setting_value,
                "updated_at": str(new_setting.updated_at)
            },
            message="设置已保存"
        )


@router.delete("/settings/{setting_id}", response_model=Response)
async def delete_chart_setting(
    setting_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login),
):
    """
    删除图表设置.
    """
    result = await db.execute(
        select(UserChartSetting).where(
            UserChartSetting.id == setting_id,
            UserChartSetting.user_id == current_user.id
        )
    )
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(status_code=404, detail="设置不存在")

    await db.delete(setting)
    await db.commit()

    return Response(
        success=True,
        message="设置已删除"
    )


@router.delete("/settings/type/{setting_type}", response_model=Response)
async def delete_chart_settings_by_type(
    setting_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login),
):
    """
    删除指定类型的所有设置.
    """
    result = await db.execute(
        select(UserChartSetting).where(
            UserChartSetting.user_id == current_user.id,
            UserChartSetting.setting_type == setting_type
        )
    )
    settings = result.scalars().all()

    for setting in settings:
        await db.delete(setting)

    await db.commit()

    return Response(
        success=True,
        message=f"已删除{len(settings)}个设置"
    )