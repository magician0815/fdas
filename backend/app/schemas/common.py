"""
统一响应Schema.

Author: FDAS Team
Created: 2026-04-03
"""

from typing import Optional, Any, List
from pydantic import BaseModel


class Response(BaseModel):
    """统一API响应格式."""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel):
    """分页响应格式."""
    success: bool
    data: List[Any]
    total: int
    page: int
    limit: int
    message: Optional[str] = None