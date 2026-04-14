"""
复权计算服务.

提供股票复权价格计算功能，支持前复权、后复权、不复权.

Author: FDAS Team
Created: 2026-04-14
"""

from typing import List, Optional, Dict, Any
from datetime import date
import math


class AdjustmentType:
    """复权类型枚举."""
    NONE = "none"      # 不复权
    FORWARD = "forward"  # 前复权
    BACKWARD = "backward"  # 后复权


class AdjustmentFactor:
    """复权因子数据结构."""

    def __init__(
        self,
        event_date: date,
        factor: float,
        dividend: float = 0.0,
        bonus_ratio: float = 0.0,
        split_ratio: float = 0.0,
        split_price: float = 0.0
    ):
        """初始化复权因子.

        Args:
            event_date: 除权除息日期
            factor: 复权因子
            dividend: 每股分红金额
            bonus_ratio: 每股送股比例（如0.1表示10送1）
            split_ratio: 每股配股比例
            split_price: 配股价格
        """
        self.event_date = event_date
        self.factor = factor
        self.dividend = dividend
        self.bonus_ratio = bonus_ratio
        self.split_ratio = split_ratio
        self.split_price = split_price


def calculate_adjustment_factor(
    prev_close: float,
    dividend: float = 0.0,
    bonus_ratio: float = 0.0,
    split_ratio: float = 0.0,
    split_price: float = 0.0
) -> float:
    """计算单次复权因子.

    简化计算公式（只考虑分红和送股）：
    复权因子 = (收盘价 - 分红) / (收盘价 * (1 + 送股比例))

    Args:
        prev_close: 除权前收盘价
        dividend: 每股分红金额
        bonus_ratio: 每股送股比例
        split_ratio: 每股配股比例
        split_price: 配股价格

    Returns:
        复权因子
    """
    if prev_close <= 0:
        return 1.0

    # 简化计算：只考虑分红和送股
    adjusted_close = prev_close - dividend
    total_ratio = 1 + bonus_ratio

    if total_ratio <= 0:
        return 1.0

    return adjusted_close / (prev_close * total_ratio)


def calculate_forward_adjusted_price(
    original_price: float,
    cumulative_factor: float
) -> float:
    """计算前复权价格.

    前复权：当前价格不变，历史价格按复权因子调整
    公式：前复权价格 = 原价格 * 累计复权因子

    Args:
        original_price: 原始价格
        cumulative_factor: 累计复权因子

    Returns:
        前复权价格
    """
    return original_price * cumulative_factor


def calculate_backward_adjusted_price(
    original_price: float,
    cumulative_factor: float
) -> float:
    """计算后复权价格.

    后复权：历史价格不变，当前价格按复权因子调整
    公式：后复权价格 = 原价格 / 累计复权因子

    Args:
        original_price: 原始价格
        cumulative_factor: 累计复权因子

    Returns:
        后复权价格
    """
    if cumulative_factor <= 0:
        return original_price
    return original_price / cumulative_factor


def round_price(price: float, precision: int = 2) -> float:
    """价格取整（按精度）.

    Args:
        price: 价格
        precision: 精度（小数位数）

    Returns:
        取整后的价格
    """
    multiplier = 10 ** precision
    return round(price * multiplier) / multiplier


def calculate_adjusted_prices(
    daily_data: List[Dict[str, Any]],
    adjustment_factors: List[AdjustmentFactor],
    adjustment_type: str,
    precision: int = 2
) -> List[Dict[str, Any]]:
    """批量计算复权价格.

    Args:
        daily_data: 原始K线数据列表，每项包含date, open, close, high, low
        adjustment_factors: 复权因子列表
        adjustment_type: 复权类型 (none/forward/backward)
        precision: 价格精度

    Returns:
        复权后的K线数据列表
    """
    if not daily_data:
        return []

    if adjustment_type == AdjustmentType.NONE:
        # 不复权，直接返回原始数据
        return [{
            "date": item.get("date"),
            "open": float(item.get("open", 0)),
            "close": float(item.get("close", 0)),
            "high": float(item.get("high", 0)),
            "low": float(item.get("low", 0))
        } for item in daily_data]

    # 构建日期到复权因子的映射
    factor_map: Dict[date, float] = {}
    for af in adjustment_factors:
        factor_map[af.event_date] = af.factor

    # 计算累计复权因子（从当前日期往历史累积）
    cumulative_factors: List[float] = []
    cumulative_factor = 1.0

    # 从最后一天往前计算
    for i in range(len(daily_data) - 1, -1, -1):
        data_item = daily_data[i]
        item_date = data_item.get("date")
        if isinstance(item_date, str):
            try:
                item_date = date.fromisoformat(item_date)
            except ValueError:
                item_date = None

        if item_date and item_date in factor_map:
            cumulative_factor *= factor_map[item_date]

        cumulative_factors.insert(0, cumulative_factor)

    # 根据复权类型计算价格
    result = []
    for i, item in enumerate(daily_data):
        factor = cumulative_factors[i]
        original_open = float(item.get("open", 0))
        original_close = float(item.get("close", 0))
        original_high = float(item.get("high", 0))
        original_low = float(item.get("low", 0))

        if adjustment_type == AdjustmentType.FORWARD:
            adjusted_open = calculate_forward_adjusted_price(original_open, factor)
            adjusted_close = calculate_forward_adjusted_price(original_close, factor)
            adjusted_high = calculate_forward_adjusted_price(original_high, factor)
            adjusted_low = calculate_forward_adjusted_price(original_low, factor)
        else:  # BACKWARD
            adjusted_open = calculate_backward_adjusted_price(original_open, factor)
            adjusted_close = calculate_backward_adjusted_price(original_close, factor)
            adjusted_high = calculate_backward_adjusted_price(original_high, factor)
            adjusted_low = calculate_backward_adjusted_price(original_low, factor)

        result.append({
            "date": item.get("date"),
            "open": round_price(adjusted_open, precision),
            "close": round_price(adjusted_close, precision),
            "high": round_price(adjusted_high, precision),
            "low": round_price(adjusted_low, precision)
        })

    return result


class AdjustmentService:
    """复权计算服务类."""

    def __init__(self):
        """初始化服务."""
        self._factor_cache: Dict[str, List[AdjustmentFactor]] = {}

    def get_adjustment_factors(
        self,
        symbol_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[AdjustmentFactor]:
        """获取指定股票的复权因子列表.

        Args:
            symbol_id: 股票ID
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            复权因子列表
        """
        # TODO: 从数据库查询除权除息事件
        # 当前返回模拟数据
        return self._get_mock_factors(symbol_id)

    def _get_mock_factors(self, symbol_id: str) -> List[AdjustmentFactor]:
        """获取模拟复权因子数据（用于测试）.

        Args:
            symbol_id: 股票ID

        Returns:
            模拟复权因子列表
        """
        # 返回空列表，实际使用时需要从数据库获取
        return []

    def calculate_adjusted_data(
        self,
        daily_data: List[Dict[str, Any]],
        symbol_id: str,
        adjustment_type: str,
        precision: int = 2
    ) -> List[Dict[str, Any]]:
        """计算复权后的K线数据.

        Args:
            daily_data: 原始K线数据
            symbol_id: 股票ID
            adjustment_type: 复权类型
            precision: 价格精度

        Returns:
            复权后的K线数据
        """
        # 获取复权因子
        factors = self.get_adjustment_factors(symbol_id)

        # 计算复权价格
        return calculate_adjusted_prices(daily_data, factors, adjustment_type, precision)

    def clear_cache(self, symbol_id: Optional[str] = None):
        """清除缓存.

        Args:
            symbol_id: 股票ID（可选，不指定则清除全部）
        """
        if symbol_id:
            self._factor_cache.pop(symbol_id, None)
        else:
            self._factor_cache.clear()

    def calculate_technical_indicators_adjusted(
        self,
        daily_data: List[Dict[str, Any]],
        ma_periods: List[int] = [5, 10, 20, 60],
        macd_params: Dict[str, int] = {"fast": 12, "slow": 26, "signal": 9}
    ) -> Dict[str, Any]:
        """基于复权价格计算技术指标.

        Args:
            daily_data: 复权后的K线数据
            ma_periods: 均线周期列表
            macd_params: MACD参数

        Returns:
            技术指标数据
        """
        from app.services.technical_service import TechnicalService

        tech_service = TechnicalService()

        # 计算均线
        ma_data = {}
        for period in ma_periods:
            closes = [item["close"] for item in daily_data]
            ma_values = tech_service.calculate_ma(closes, period)
            ma_data[f"ma{period}"] = [{"value": v} for v in ma_values]

        # 计算MACD
        closes = [item["close"] for item in daily_data]
        macd_data = tech_service.calculate_macd(
            closes,
            macd_params.get("fast", 12),
            macd_params.get("slow", 26),
            macd_params.get("signal", 9)
        )

        return {
            "ma": ma_data,
            "macd": macd_data
        }