"""
数据源配置向导API.

提供数据源配置向导的7个步骤接口。

Author: FDAS Team
Created: 2026-04-21
"""

from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.schemas.common import Response
from app.services.datasource_wizard_service import get_wizard_service

router = APIRouter()


# ==================== 请求模型 ====================

class Step1Request(BaseModel):
    """步骤1：基础信息"""
    datasource_name: str = Field(..., min_length=1, max_length=100, description="数据源名称")
    market_id: UUID = Field(..., description="市场ID")


class Step2Request(BaseModel):
    """步骤2：API配置"""
    session_id: UUID = Field(..., description="会话ID")
    api_base_url: str = Field(..., min_length=1, description="API基础URL")
    api_method: str = Field(default="GET", description="请求方法")
    api_timeout: int = Field(default=30, ge=5, le=300, description="超时时间(秒)")
    api_headers: Optional[Dict[str, str]] = Field(default=None, description="请求头")


class Step3Request(BaseModel):
    """步骤3：端点探测"""
    session_id: UUID = Field(..., description="会话ID")
    api_base_url: str = Field(..., description="API基础URL")
    api_method: str = Field(default="GET", description="请求方法")
    api_timeout: int = Field(default=30, description="超时时间")
    api_headers: Optional[Dict] = Field(default=None, description="请求头")
    test_params: Optional[Dict] = Field(default=None, description="测试参数")


class Step4Request(BaseModel):
    """步骤4：数据预览"""
    session_id: UUID = Field(..., description="会话ID")
    endpoint_url: str = Field(..., description="端点URL")
    api_method: str = Field(default="GET", description="请求方法")
    api_timeout: int = Field(default=30, description="超时时间")
    api_headers: Optional[Dict] = Field(default=None, description="请求头")
    params: Optional[Dict] = Field(default=None, description="请求参数")


class Step5Request(BaseModel):
    """步骤5：字段识别"""
    session_id: UUID = Field(..., description="会话ID")
    sample_data: list = Field(..., description="样本数据列表")


class Step6Request(BaseModel):
    """步骤6：测试采集"""
    session_id: UUID = Field(..., description="会话ID")
    config: Dict[str, Any] = Field(..., description="完整配置")
    symbol_code: str = Field(default="TEST", description="测试用货币对")


class Step7Request(BaseModel):
    """步骤7：保存数据源"""
    session_id: UUID = Field(..., description="会话ID")


# ==================== API端点 ====================

@router.post("/wizard/step1", response_model=Response)
async def wizard_step1_validate(
    request: Step1Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    步骤1：验证基础信息。

    验证数据源名称唯一性。
    """
    from sqlalchemy import select
    from app.models.datasource import DataSource

    # 检查名称唯一性
    result = await db.execute(
        select(DataSource).where(DataSource.name == request.datasource_name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="数据源名称已存在，请更换"
        )

    # 创建会话
    wizard_service = get_wizard_service(db)
    session = await wizard_service.create_session(admin.id)

    # 保存步骤1数据
    await wizard_service.update_session_step(
        session.id,
        step=1,
        step_data={
            "datasource_name": request.datasource_name,
            "market_id": request.market_id,
        },
    )

    return Response(
        success=True,
        data={"session_id": str(session.id), "current_step": 1},
        message="名称验证通过",
    )


@router.post("/wizard/step2-test", response_model=Response)
async def wizard_step2_test_connection(
    request: Step2Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    步骤2：测试API连接。

    验证API地址是否可访问。
    """
    wizard_service = get_wizard_service(db)

    success, error_msg, response_data = await wizard_service.test_api_connection(
        base_url=request.api_base_url,
        method=request.api_method,
        timeout=request.api_timeout,
        headers=request.api_headers,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    # 保存步骤2数据
    await wizard_service.update_session_step(
        request.session_id,
        step=2,
        step_data={
            "api_base_url": request.api_base_url,
            "api_method": request.api_method,
            "api_timeout": request.api_timeout,
            "api_headers": request.api_headers,
        },
    )

    return Response(
        success=True,
        data={"session_id": str(request.session_id), "current_step": 2},
        message="API连接测试通过",
    )


@router.post("/wizard/step3-probe", response_model=Response)
async def wizard_step3_probe_endpoints(
    request: Step3Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    步骤3：探测可用端点。

    自动发现API中可用的数据接口。
    """
    wizard_service = get_wizard_service(db)

    success, error_msg, endpoints_list = await wizard_service.probe_endpoints(
        base_url=request.api_base_url,
        method=request.api_method,
        timeout=request.api_timeout,
        headers=request.api_headers,
        test_params=request.test_params,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    # 保存端点列表
    await wizard_service.update_session_step(
        request.session_id,
        step=3,
        step_data={"available_endpoints": endpoint_list},
    )

    return Response(
        success=True,
        data={
            "session_id": str(request.session_id),
            "current_step": 3,
            "endpoints": endpoint_list,
        },
        message=f"发现 {len(endpoint_list)} 个可用端点",
    )


@router.post("/wizard/step4-preview", response_model=Response)
async def wizard_step4_preview_data(
    request: Step4Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    步骤4：获取数据预览。

    获取样本数据供用户确认。
    """
    wizard_service = get_wizard_service(db)

    success, error_msg, sample_data = await wizard_service.fetch_sample_data(
        endpoint_url=request.endpoint_url,
        method=request.api_method,
        timeout=request.api_timeout,
        headers=request.api_headers,
        params=request.params,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    # 保存样本数据
    await wizard_service.update_session_step(
        request.session_id,
        step=4,
        step_data={"sample_data": sample_data},
    )

    return Response(
        success=True,
        data={
            "session_id": str(request.session_id),
            "current_step": 4,
            "sample_data": sample_data,
        },
        message="获取到预览数据",
    )


@router.post("/wizard/step5-detect", response_model=Response)
async def wizard_step5_detect_fields(
    request: Step5Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    步骤5：自动识别字段映射。

    分析样本数据自动识别OHLC等字段。
    """
    wizard_service = get_wizard_service(db)

    success, error_msg, field_mapping = await wizard_service.detect_field_mapping(
        sample_data=request.sample_data,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    # 保存字段映射
    await wizard_service.update_session_step(
        request.session_id,
        step=5,
        step_data={"field_mapping": field_mapping},
    )

    return Response(
        success=True,
        data={
            "session_id": str(request.session_id),
            "current_step": 5,
            "field_mapping": field_mapping,
        },
        message="字段识别完成",
    )


@router.post("/wizard/step6-test-collect", response_model=Response)
async def wizard_step6_test_collection(
    request: Step6Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    步骤6：测试采集。

    验证完整配置可以采集到数据。
    """
    wizard_service = get_wizard_service(db)

    success, message, count = await wizard_service.test_collection(
        config=request.config,
        symbol_code=request.symbol_code,
    )

    # 保存测试结果
    await wizard_service.update_session_step(
        request.session_id,
        step=6,
        step_data={"test_result": {"success": success, "message": message, "count": count}},
    )

    return Response(
        success=success,
        data={
            "session_id": str(request.session_id),
            "current_step": 6,
            "test_result": {"message": message, "count": count},
        },
        message=message,
    )


@router.post("/wizard/step7-save", response_model=Response)
async def wizard_step7_save_datasource(
    request: Step7Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    步骤7：确认保存。

    将配置保存为数据源记录。
    """
    wizard_service = get_wizard_service(db)

    success, error_msg, datasource_id = await wizard_service.save_datasource(
        session_id=request.session_id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    return Response(
        success=True,
        data={
            "datasource_id": str(datasource_id),
            "current_step": 7,
        },
        message="数据源创建成功",
    )


@router.get("/wizard/{session_id}", response_model=Response)
async def wizard_get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    获取向导会话状态。
    """
    wizard_service = get_wizard_service(db)
    session = await wizard_service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在",
        )

    return Response(
        success=True,
        data={
            "session_id": str(session.id),
            "current_step": session.current_step,
            "status": session.status,
            "step_data": session.to_step_data(session.current_step),
        },
    )