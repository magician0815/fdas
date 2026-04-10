"""
技术指标计算服务.

使用TA-Lib计算MA、MACD等技术指标.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-10 - 适配ForexDaily模型
"""

from typing import List, Dict
import logging

from app.models.forex_daily import ForexDaily
from app.config.settings import settings

logger = logging.getLogger(__name__)


class TechnicalService:
    """
    技术指标计算服务.

    使用TA-Lib计算MA、MACD等技术指标.
    """

    def calculate_ma(
        self,
        data: List[ForexDaily],
        period: int = None,
    ) -> List[Dict]:
        """
        计算MA均线.

        Args:
            data: 日线数据列表
            period: 周期（默认使用配置）

        Returns:
            List[Dict]: MA值列表
        """
        if period is None:
            period = settings.DEFAULT_MA_PERIOD

        if len(data) < period:
            return []

        # 简单移动平均计算（不依赖TA-Lib）
        # 数据已按日期升序排列（由服务层保证）
        close_prices = [float(d.close) for d in data if d.close]

        result = []
        for i in range(period - 1, len(close_prices)):
            ma_value = sum(close_prices[i - period + 1:i + 1]) / period
            result.append({
                "index": i,
                "value": round(ma_value, 4),
            })

        return result

    def calculate_macd(
        self,
        data: List[ForexDaily],
        fast: int = None,
        slow: int = None,
        signal: int = None,
    ) -> Dict:
        """
        计算MACD指标.

        Args:
            data: 日线数据列表
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            Dict: MACD数据（macd, signal, hist）
        """
        if fast is None:
            fast = settings.DEFAULT_MACD_FAST
        if slow is None:
            slow = settings.DEFAULT_MACD_SLOW
        if signal is None:
            signal = settings.DEFAULT_MACD_SIGNAL

        # TODO: 实现MACD计算（需要TA-Lib）
        # 暂时返回空数据
        return {
            "macd": [],
            "signal": [],
            "hist": [],
        }

    def calculate_all_indicators(
        self,
        data: List[ForexDaily],
    ) -> Dict:
        """
        计算所有技术指标.

        Args:
            data: 日线数据列表

        Returns:
            Dict: 所有技术指标数据
        """
        return {
            "ma": self.calculate_ma(data),
            "macd": self.calculate_macd(data),
        }


# 全局服务实例
technical_service = TechnicalService()