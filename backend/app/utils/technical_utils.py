"""
技术指标辅助函数.

提供EMA等通用计算函数，避免代码重复.

Author: FDAS Team
Created: 2026-04-16
"""

from typing import List


def calculate_ema(prices: List[float], period: int) -> List[float]:
    """
    计算指数移动平均线（EMA）.

    使用SMA作为初始值，然后递归计算EMA.
    公式: EMA(t) = price(t) * k + EMA(t-1) * (1-k), k = 2/(period+1)

    Args:
        prices: 价格列表（按时间升序排列）
        period: EMA周期

    Returns:
        List[float]: EMA值列表

    Note:
        Caller ensures len(prices) >= period before calling.
    """
    if not prices or period <= 0 or len(prices) < period:
        return []

    # 第一个EMA值用SMA
    sma = sum(prices[:period]) / period
    ema_values: List[float] = [sma]

    multiplier = 2 / (period + 1)
    for i in range(period, len(prices)):
        new_ema = (prices[i] - ema_values[-1]) * multiplier + ema_values[-1]
        ema_values.append(new_ema)

    return ema_values