"""
采集任务Schema.

定义采集任务相关的请求和响应模型.

Author: FDAS Team
Created: 2026-04-10
Updated: 2026-04-11 - 新增CollectionTaskValidateRequest和ValidateResult模型
"""

from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class CollectionTaskBase(BaseModel):
    """采集任务基础模型."""
    name: str = Field(..., description="任务名称", max_length=100)
    datasource_id: UUID = Field(..., description="数据源ID")
    market_id: UUID = Field(..., description="目标市场ID")
    symbol_id: UUID = Field(..., description="目标标的ID")
    start_date: Optional[date] = Field(None, description="采集开始日期")
    end_date: Optional[date] = Field(None, description="采集结束日期")
    cron_expr: Optional[str] = Field(None, description="Cron定时表达式", max_length=100)
    is_enabled: bool = Field(default=False, description="是否启用")


class CollectionTaskCreate(CollectionTaskBase):
    """创建采集任务请求."""
    pass


class CollectionTaskUpdate(BaseModel):
    """更新采集任务请求."""
    name: Optional[str] = Field(None, description="任务名称", max_length=100)
    datasource_id: Optional[UUID] = Field(None, description="数据源ID")
    market_id: Optional[UUID] = Field(None, description="目标市场ID")
    symbol_id: Optional[UUID] = Field(None, description="目标标的ID")
    start_date: Optional[date] = Field(None, description="采集开始日期")
    end_date: Optional[date] = Field(None, description="采集结束日期")
    cron_expr: Optional[str] = Field(None, description="Cron定时表达式", max_length=100)
    is_enabled: Optional[bool] = Field(None, description="是否启用")


class CollectionTaskValidateRequest(BaseModel):
    """采集任务参数校验请求."""
    name: Optional[str] = Field(None, description="任务名称", max_length=100)
    datasource_id: UUID = Field(..., description="数据源ID")
    market_id: UUID = Field(..., description="目标市场ID")
    symbol_id: UUID = Field(..., description="目标标的ID")
    start_date: Optional[date] = Field(None, description="采集开始日期")
    end_date: Optional[date] = Field(None, description="采集结束日期")
    cron_expr: Optional[str] = Field(None, description="Cron定时表达式", max_length=100)


class ValidateResult(BaseModel):
    """校验结果模型."""
    valid: bool = Field(default=True, description="是否通过校验")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")
    warnings: List[str] = Field(default_factory=list, description="警告信息列表")
    info: dict = Field(default_factory=dict, description="附加信息")


class CollectionTaskResponse(BaseModel):
    """采集任务响应."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    datasource_id: UUID
    market_id: UUID
    symbol_id: UUID
    start_date: Optional[date]
    end_date: Optional[date]
    cron_expr: Optional[str]
    is_enabled: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    last_status: Optional[str]
    last_message: Optional[str]
    last_records_count: int
    created_at: datetime
    updated_at: datetime


class CollectionTaskLogResponse(BaseModel):
    """采集任务日志响应."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    run_at: datetime
    status: str
    records_count: int
    message: Optional[str]
    duration_ms: Optional[int]
    created_at: datetime


class TaskExecuteRequest(BaseModel):
    """手动执行任务请求."""
    force: bool = Field(default=False, description="是否强制执行（忽略日期限制）")


class TaskExecuteResponse(BaseModel):
    """手动执行任务响应."""
    task_id: UUID
    task_name: str
    symbol: str
    status: str
    records_count: int
    message: str
    duration_ms: Optional[int]