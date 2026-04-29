"""
图表模板API路由.

提供图表模板的保存、加载、分享等功能.

Author: FDAS Team
Created: 2026-04-14
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import require_login
from app.models.user import User
from app.schemas.common import Response
from app.services.chart_template_service import chart_template_service

router = APIRouter()


# Pydantic模型定义
class TemplateCreateRequest(BaseModel):
    """创建模板请求."""
    name: str
    description: str = ""
    config: Dict[str, Any]
    is_public: bool = False


class TemplateUpdateRequest(BaseModel):
    """更新模板请求."""
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class ApplyTemplateRequest(BaseModel):
    """应用模板请求."""
    symbol_id: str


@router.post("/templates", response_model=Response)
async def create_template(
    request: TemplateCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login)
):
    """
    创建图表模板.

    保存当前图表配置（均线、指标、画线、主题等）为模板.
    """
    template = await chart_template_service.save_template(
        db=db,
        user_id=current_user.id,
        template_name=request.name,
        template_config=request.config,
        description=request.description,
        is_public=request.is_public
    )

    return Response(
        success=True,
        data=template.to_dict(),
        message="模板保存成功"
    )


@router.get("/templates", response_model=Response)
async def list_templates(
    include_public: bool = Query(default=False, description="是否包含公开模板"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login)
):
    """
    获取模板列表.

    返回用户自己的模板，可选包含公开模板.
    """
    # 获取用户模板
    user_templates = await chart_template_service.list_user_templates(db, current_user.id)

    result = [t.to_dict() for t in user_templates]

    # 如果需要包含公开模板
    if include_public:
        public_templates = await chart_template_service.list_public_templates(db)
        result.extend([t.to_dict() for t in public_templates])

    return Response(
        success=True,
        data=result,
        meta={"total": len(result)}
    )


@router.get("/templates/{template_id}", response_model=Response)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login)
):
    """
    获取模板详情.
    """
    template = await chart_template_service.load_template(db, template_id)

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    return Response(
        success=True,
        data=template.to_dict()
    )


@router.put("/templates/{template_id}", response_model=Response)
async def update_template(
    template_id: str,
    request: TemplateUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login)
):
    """
    更新模板.

    更新模板名称、描述或配置.
    """
    # 构建更新字典
    updates = {}
    if request.name is not None:
        updates["name"] = request.name
    if request.description is not None:
        updates["description"] = request.description
    if request.config is not None:
        updates["config"] = request.config
    if request.is_public is not None:
        updates["is_public"] = request.is_public

    template = await chart_template_service.update_template(
        db=db,
        user_id=current_user.id,
        template_id=template_id,
        updates=updates
    )

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在或无权限更新")

    return Response(
        success=True,
        data=template.to_dict(),
        message="模板更新成功"
    )


@router.delete("/templates/{template_id}", response_model=Response)
async def delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login)
):
    """
    删除模板.
    """
    success = await chart_template_service.delete_template(
        db=db,
        user_id=current_user.id,
        template_id=template_id
    )

    if not success:
        raise HTTPException(status_code=404, detail="模板不存在或无权限删除")

    return Response(
        success=True,
        message="模板删除成功"
    )


@router.post("/templates/{template_id}/apply", response_model=Response)
async def apply_template(
    template_id: str,
    request: ApplyTemplateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login)
):
    """
    应用模板到指定标的.
    """
    success = await chart_template_service.apply_template_to_chart(
        db=db,
        user_id=current_user.id,
        template_id=template_id,
        symbol_id=request.symbol_id
    )

    if not success:
        raise HTTPException(status_code=404, detail="模板不存在")

    return Response(
        success=True,
        message="模板应用成功"
    )


@router.get("/templates/{template_id}/share", response_model=Response)
async def get_template_share_link(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_login)
):
    """
    获取模板分享链接.
    """
    template = await chart_template_service.load_template(db, template_id)

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 检查是否有分享权限（是自己的模板或公开模板）
    if template.creator_id != current_user.id and not template.is_public:
        raise HTTPException(status_code=403, detail="无权限分享此模板")

    share_link = chart_template_service.generate_share_link(template_id)

    return Response(
        success=True,
        data={
            "share_link": share_link,
            "template_id": template_id,
            "is_public": template.is_public
        }
    )