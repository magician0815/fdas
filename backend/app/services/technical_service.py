"""
技术指标计算服务.

使用TA-Lib计算MA、MACD等技术指标.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-14 - 返回多条均线和MACD完整数据
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

    def calculate_all_ma(
        self,
        data: List[ForexDaily],
        periods: List[int] = None,
    ) -> Dict[str, List[Dict]]:
        """
        计算多条MA均线.

        Args:
            data: 日线数据列表
            periods: 周期列表（默认 [5, 10, 20, 60]）

        Returns:
            Dict[str, List[Dict]]: 多条MA数据，如 { "ma5": [...], "ma10": [...] }
        """
        if periods is None:
            periods = [5, 10, 20, 60]

        result = {}
        close_prices = [float(d.close) for d in data if d.close]

        for period in periods:
            key = f"ma{period}"
            ma_values = []

            if len(close_prices) >= period:
                for i in range(period - 1, len(close_prices)):
                    ma_value = sum(close_prices[i - period + 1:i + 1]) / period
                    ma_values.append({
                        "value": round(ma_value, 4),
                    })

            result[key] = ma_values

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
            fast: 快线周期（默认12）
            slow: 慢线周期（默认26）
            signal: 信号线周期（默认9）

        Returns:
            Dict: MACD数据（dif, dea, macd）
        """
        if fast is None:
            fast = settings.DEFAULT_MACD_FAST
        if slow is None:
            slow = settings.DEFAULT_MACD_SLOW
        if signal is None:
            signal = settings.DEFAULT_MACD_SIGNAL

        close_prices = [float(d.close) for d in data if d.close]

        if len(close_prices) < slow + signal:
            return {
                "dif": [],
                "dea": [],
                "macd": [],
            }

        # 计算EMA
        def ema(prices, period):
            """计算EMA."""
            if len(prices) < period:
                return []

            # 第一个EMA值用SMA
            sma = sum(prices[:period]) / period
            ema_values = [sma]

            multiplier = 2 / (period + 1)
            for i in range(period, len(prices)):
                new_ema = (prices[i] - ema_values[-1]) * multiplier + ema_values[-1]
                ema_values.append(new_ema)

            return ema_values

        # 计算DIF = EMA(fast) - EMA(slow)
        ema_fast = ema(close_prices, fast)
        ema_slow = ema(close_prices, slow)

        # DIF从 slow-1 开始有数据
        dif_values = []
        for i in range(slow - 1, len(ema_fast)):
            dif = ema_fast[i] - ema_slow[i - (slow - fast)]
            dif_values.append(round(dif, 4))

        # 计算DEA = EMA(DIF, signal)
        if len(dif_values) < signal:
            return {
                "dif": dif_values,
                "dea": [],
                "macd": [],
            }

        dea_values = ema(dif_values, signal)

        # 计算MACD柱 = DIF - DEA
        macd_values = []
        for i in range(len(dea_values)):
            macd = dif_values[i + signal - 1] - dea_values[i]
            macd_values.append(round(macd, 4))

        # 补齐DIF和DEA的长度（MACD柱需要signal-1个前置数据）
        dif_result = dif_values[signal - 1:] if len(dif_values) >= signal else []

        return {
            "dif": dif_result,
            "dea": [round(v, 4) for v in dea_values],
            "macd": macd_values,
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
            "ma": self.calculate_all_ma(data),
            "macd": self.calculate_macd(data),
            "vol": self.calculate_volume_ma(data),
        }

    def calculate_volume_ma(
        self,
        data: List[ForexDaily],
        periods: List[int] = None,
    ) -> Dict[str, List[Dict]]:
        """
        计算成交量均线.

        Args:
            data: 日线数据列表
            periods: 周期列表（默认 [5, 10]）

        Returns:
            Dict[str, List[Dict]]: 成交量均线数据
        """
        if periods is None:
            periods = [5, 10]

        result = {}
        volumes = [float(d.volume) if d.volume else 0 for d in data]

        for period in periods:
            key = f"vol{period}"
            vol_values = []

            if len(volumes) >= period:
                for i in range(period - 1, len(volumes)):
                    vol_ma = sum(volumes[i - period + 1:i + 1]) / period
                    vol_values.append({
                        "value": round(vol_ma, 0),
                    })

            result[key] = vol_values

        return result


# 全局服务实例
technical_service = TechnicalService()