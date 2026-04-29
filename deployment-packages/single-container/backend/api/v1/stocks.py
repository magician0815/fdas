"""
股票数据API.

提供股票复权数据、除权除息事件等接口.

Author: FDAS Team
Created: 2026-04-14
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from datetime import date
from pydantic import BaseModel

from app.services.adjustment_service import AdjustmentService, AdjustmentType


router = APIRouter(prefix="/stocks", tags=["股票数据"])


# 请求/响应模型
class AdjustmentRequest(BaseModel):
    """复权请求模型."""
    symbol_id: str
    adjustment_type: str = "none"  # none/forward/backward
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class AdjustmentResponse(BaseModel):
    """复权响应模型."""
    symbol_id: str
    adjustment_type: str
    data: List[dict]
    count: int


class DividendEvent(BaseModel):
    """除权除息事件模型."""
    event_id: str
    symbol_id: str
    event_date: str
    event_type: str  # dividend/split/bonus
    dividend_per_share: Optional[float] = None
    split_ratio: Optional[float] = None
    bonus_per_share: Optional[float] = None
    adjustment_factor: float


class DividendEventsResponse(BaseModel):
    """除权除息事件响应模型."""
    symbol_id: str
    events: List[DividendEvent]
    count: int


@router.get("/adjustment", response_model=AdjustmentResponse)
async def get_adjustment_data(
    symbol_id: str = Query(..., description="股票ID"),
    adjustment_type: str = Query("none", description="复权类型：none/forward/backward"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
):
    """获取复权后的K线数据.

    Args:
        symbol_id: 股票ID
        adjustment_type: 复权类型
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        复权后的K线数据
    """
    # 验证复权类型
    valid_types = [AdjustmentType.NONE, AdjustmentType.FORWARD, AdjustmentType.BACKWARD]
    if adjustment_type not in valid_types:
        raise HTTPException(status_code=400, detail="无效的复权类型")

    # TODO: 从数据库获取原始K线数据
    # 当前返回模拟数据
    adjustment_service = AdjustmentService()

    # 模拟原始数据
    mock_data = [
        {"date": "2026-01-01", "open": 10.0, "close": 10.5, "high": 11.0, "low": 9.5},
        {"date": "2026-01-02", "open": 10.5, "close": 11.0, "high": 11.5, "low": 10.0},
    ]

    # 计算复权价格
    adjusted_data = adjustment_service.calculate_adjusted_data(
        mock_data,
        symbol_id,
        adjustment_type
    )

    return AdjustmentResponse(
        symbol_id=symbol_id,
        adjustment_type=adjustment_type,
        data=adjusted_data,
        count=len(adjusted_data)
    )


@router.get("/dividend-events", response_model=DividendEventsResponse)
async def get_dividend_events(
    symbol_id: str = Query(..., description="股票ID"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
):
    """获取除权除息事件列表.

    Args:
        symbol_id: 股票ID
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        除权除息事件列表
    """
    # TODO: 从数据库查询除权除息事件
    # 当前返回模拟数据
    mock_events = []

    return DividendEventsResponse(
        symbol_id=symbol_id,
        events=mock_events,
        count=len(mock_events)
    )


@router.get("/market-type")
async def get_market_type(
    symbol_code: str = Query(..., description="股票代码"),
    symbol_name: Optional[str] = Query(None, description="股票名称")
):
    """识别股票市场类型.

    Args:
        symbol_code: 股票代码
        symbol_name: 股票名称（可选）

    Returns:
        市场类型信息
    """
    from app.utils.stock_utils import identify_market_type

    market_type = identify_market_type(symbol_code, symbol_name)

    return {
        "symbol_code": symbol_code,
        "symbol_name": symbol_name,
        "market_type": market_type,
        "config": {
            "limit_up_threshold": get_limit_threshold(market_type, "up"),
            "limit_down_threshold": get_limit_threshold(market_type, "down"),
            "has_limit": market_type != "forex",
            "need_adjustment": market_type != "forex"
        }
    }


def get_limit_threshold(market_type: str, direction: str) -> float:
    """获取涨跌停阈值.

    Args:
        market_type: 市场类型
        direction: up/down

    Returns:
        阈值百分比
    """
    thresholds = {
        "stock_a": {"up": 10, "down": 10},
        "stock_kcb": {"up": 20, "down": 20},
        "stock_cyb": {"up": 20, "down": 20},
        "stock_st": {"up": 5, "down": 5},
        "stock_bjb": {"up": 30, "down": 30},
        "forex": {"up": 0, "down": 0}
    }

    config = thresholds.get(market_type, thresholds["forex"])
    return config.get(direction, 0)