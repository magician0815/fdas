"""
技术指标计算服务.

使用TA-Lib计算MA、MACD等技术指标.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-14 - 返回多条均线和MACD完整数据
Updated: 2026-04-16 - 使用calculate_ema公共函数
"""

from typing import List, Dict
import logging

from app.models.forex_daily import ForexDaily
from app.config.settings import settings
from app.utils.technical_utils import calculate_ema

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
            periods: 周期列表（默认 [5, 10, 20, 30, 60, 120, 240]）

        Returns:
            Dict[str, List[Dict]]: 多条MA数据，如 { "ma5": [...], "ma10": [...] }
            每条MA数组长度与输入数据一致，前period-1个元素为第一个有效MA值。
        """
        if periods is None:
            periods = [5, 10, 20, 30, 60, 120, 240]

        result = {}
        close_prices = [float(d.close) for d in data if d.close]
        total_len = len(close_prices)

        for period in periods:
            key = f"ma{period}"
            ma_values = []

            if total_len < period:
                # 数据不足，返回与输入长度一致的None数组
                result[key] = [{"value": None}] * total_len
                continue

            # 计算第一个有效MA值（位于index period-1的位置）
            first_ma = sum(close_prices[:period]) / period

            # 前period-1个元素用第一个MA值填充（保证长度对齐）
            # 注意：这填充了index 0到period-2的位置（共period-1个元素）
            ma_values.extend([{"value": round(first_ma, 4)}] * (period - 1))

            # 从period-1开始计算后续MA值（包含第一个有效MA位置）
            # 这样总共 (period-1) + (total_len - period + 1) = total_len 个元素
            for i in range(period - 1, total_len):
                ma_value = sum(close_prices[i - period + 1:i + 1]) / period
                ma_values.append({"value": round(ma_value, 4)})

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
            fast: 快线周期（默认12，必须>0）
            slow: 慢线周期（默认26，必须>0）
            signal: 信号线周期（默认9，必须>0）

        Returns:
            Dict: MACD数据（dif, dea, macd），长度与输入数据一致，前面用None填充

        Raises:
            ValueError: 参数无效（负数或零）
        """
        if fast is None:
            fast = settings.DEFAULT_MACD_FAST
        if slow is None:
            slow = settings.DEFAULT_MACD_SLOW
        if signal is None:
            signal = settings.DEFAULT_MACD_SIGNAL

        # 参数验证：周期必须为正整数
        if fast <= 0 or slow <= 0 or signal <= 0:
            raise ValueError(f"MACD参数必须为正整数: fast={fast}, slow={slow}, signal={signal}")

        close_prices = [float(d.close) for d in data if d.close]
        total_len = len(close_prices)

        if total_len < slow + signal:
            # 数据不足，返回与输入长度一致的None数组
            return {
                "dif": [None] * total_len,
                "dea": [None] * total_len,
                "macd": [None] * total_len,
            }

        # 计算EMA，现在返回与close_prices长度一致的数组
        ema_fast = calculate_ema(close_prices, fast)
        ema_slow = calculate_ema(close_prices, slow)

        # DIF = EMA(fast) - EMA(slow)
        # EMA现在与close_prices长度一致，直接相减即可
        dif_values = []
        for i in range(total_len):
            dif = ema_fast[i] - ema_slow[i]
            dif_values.append(round(dif, 4))

        # 计算DEA = EMA(DIF, signal)
        # DEA从第signal-1个DIF开始有有效值
        dea_full = calculate_ema(dif_values, signal)

        # 计算MACD柱 = DIF - DEA
        macd_values = []
        for i in range(total_len):
            macd = dif_values[i] - dea_full[i]
            macd_values.append(round(macd, 4))

        # MACD有效数据从第 slow + signal - 1 条开始（即第34条，索引33）
        # 前34-1=33个元素设为None
        offset = slow + signal - 1  # = 34
        dif_aligned = [None] * (offset - 1) + dif_values[offset - 1:]
        dea_aligned = [None] * (offset - 1) + dea_full[offset - 1:]
        macd_aligned = [None] * (offset - 1) + macd_values[offset - 1:]

        return {
            "dif": dif_aligned,
            "dea": dea_aligned,
            "macd": macd_aligned,
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