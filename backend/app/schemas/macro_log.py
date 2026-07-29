"""
宏观采集日志 Pydantic Schema.

Author: FDAS Team
Created: 2026-07-29
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class MacroLogResponse(BaseModel):
    """采集日志响应."""
    id: UUID
    config_id: UUID
    run_at: datetime
    status: str
    records_count: int
    message: Optional[str]
    duration_ms: Optional[int]
    is_full: bool
    error_detail: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class MacroLogListResponse(BaseModel):
    """采集日志列表响应."""
    success: bool = True
    data: list[MacroLogResponse]
    total: int
