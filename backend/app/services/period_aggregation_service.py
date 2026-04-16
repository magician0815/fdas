"""
周期聚合计算服务.

基于日线数据聚合计算周K、月K数据.

Author: FDAS Team
Created: 2026-04-14
Updated: 2026-04-16 - 使用calculate_ema公共函数
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from collections import defaultdict
import calendar

from app.utils.technical_utils import calculate_ema


class PeriodType:
    """周期类型枚举."""
    DAILY = "daily"      # 日线
    WEEKLY = "weekly"    # 周线
    MONTHLY = "monthly"  # 月线
    MINUTE_1 = "1"       # 1分钟
    MINUTE_5 = "5"       # 5分钟
    MINUTE_15 = "15"     # 15分钟
    MINUTE_30 = "30"     # 30分钟
    MINUTE_60 = "60"     # 60分钟（小时线）


def get_week_bounds(d: date) -> tuple:
    """获取指定日期所在周的起始和结束日期.

    Args:
        d: 日期

    Returns:
        tuple: (周一日期, 周日日期)
    """
    # 周一为一周的开始（weekday()返回0-6，0为周一）
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def get_month_bounds(d: date) -> tuple:
    """获取指定日期所在月的起始和结束日期.

    Args:
        d: 日期

    Returns:
        tuple: (月初日期, 月末日期)
    """
    first_day = date(d.year, d.month, 1)
    last_day = date(d.year, d.month, calendar.monthrange(d.year, d.month)[1])
    return first_day, last_day


def aggregate_to_weekly(daily_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """将日线数据聚合为周K数据.

    聚合规则：
    - 开盘价：周一的开盘价（该周第一根K线的开盘价）
    - 收盘价：周五的收盘价（该周最后一根K线的收盘价）
    - 最高价：该周所有K线的最高价
    - 最低价：该周所有K线的最低价
    - 成交量：该周所有K线成交量之和

    Args:
        daily_data: 日线数据列表，每项包含date, open, close, high, low, volume

    Returns:
        周K数据列表
    """
    if not daily_data:
        return []

    # 按周分组
    weekly_groups: Dict[str, List[Dict]] = defaultdict(list)

    for item in daily_data:
        item_date = item.get("date")
        if isinstance(item_date, str):
            try:
                item_date = date.fromisoformat(item_date)
            except ValueError:
                continue
        elif isinstance(item_date, datetime):
            item_date = item_date.date()

        if not item_date:
            continue

        # 获取周起始日期作为分组键
        monday, _ = get_week_bounds(item_date)
        weekly_groups[monday.isoformat()].append(item)

    # 聚合每组数据
    weekly_data = []

    for week_start, week_items in sorted(weekly_groups.items()):
        # 按日期排序
        sorted_items = sorted(week_items, key=lambda x: x.get("date", ""))

        # 计算聚合值
        opens = [float(item.get("open", 0)) for item in sorted_items]
        closes = [float(item.get("close", 0)) for item in sorted_items]
        highs = [float(item.get("high", 0)) for item in sorted_items]
        lows = [float(item.get("low", 0)) for item in sorted_items]
        volumes = [int(item.get("volume", 0)) for item in sorted_items]

        # 开盘价：第一根K线的开盘价
        weekly_open = opens[0] if opens else 0
        # 收盘价：最后一根K线的收盘价
        weekly_close = closes[-1] if closes else 0
        # 最高价：所有K线的最高价
        weekly_high = max(highs) if highs else 0
        # 最低价：所有K线的最低价
        weekly_low = min(lows) if lows else 0
        # 成交量：总和
        weekly_volume = sum(volumes)

        # 计算涨跌幅
        if weekly_open > 0:
            change_pct = (weekly_close - weekly_open) / weekly_open * 100
            amplitude = (weekly_high - weekly_low) / weekly_open * 100
        else:
            change_pct = 0
            amplitude = 0

        # 获取周结束日期
        week_start_date = date.fromisoformat(week_start)
        week_end_date = week_start_date + timedelta(days=6)

        weekly_data.append({
            "date": week_start,  # 使用周一作为周K日期
            "week_start": week_start,
            "week_end": week_end_date.isoformat(),
            "open": weekly_open,
            "close": weekly_close,
            "high": weekly_high,
            "low": weekly_low,
            "volume": weekly_volume,
            "change_pct": round(change_pct, 4),
            "amplitude": round(amplitude, 4),
            "days": len(sorted_items)  # 该周包含的交易天数
        })

    return weekly_data


def aggregate_to_monthly(daily_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """将日线数据聚合为月K数据.

    聚合规则：
    - 开盘价：月初的开盘价（该月第一根K线的开盘价）
    - 收盘价：月末的收盘价（该月最后一根K线的收盘价）
    - 最高价：该月所有K线的最高价
    - 最低价：该月所有K线的最低价
    - 成交量：该月所有K线成交量之和

    Args:
        daily_data: 日线数据列表

    Returns:
        月K数据列表
    """
    if not daily_data:
        return []

    # 按月分组
    monthly_groups: Dict[str, List[Dict]] = defaultdict(list)

    for item in daily_data:
        item_date = item.get("date")
        if isinstance(item_date, str):
            try:
                item_date = date.fromisoformat(item_date)
            except ValueError:
                continue
        elif isinstance(item_date, datetime):
            item_date = item_date.date()

        if not item_date:
            continue

        # 使用月初日期作为分组键
        first_day, _ = get_month_bounds(item_date)
        monthly_groups[first_day.isoformat()].append(item)

    # 聚合每组数据
    monthly_data = []

    for month_start, month_items in sorted(monthly_groups.items()):
        # 按日期排序
        sorted_items = sorted(month_items, key=lambda x: x.get("date", ""))

        # 计算聚合值
        opens = [float(item.get("open", 0)) for item in sorted_items]
        closes = [float(item.get("close", 0)) for item in sorted_items]
        highs = [float(item.get("high", 0)) for item in sorted_items]
        lows = [float(item.get("low", 0)) for item in sorted_items]
        volumes = [int(item.get("volume", 0)) for item in sorted_items]

        # 开盘价：第一根K线的开盘价
        monthly_open = opens[0] if opens else 0
        # 收盘价：最后一根K线的收盘价
        monthly_close = closes[-1] if closes else 0
        # 最高价：所有K线的最高价
        monthly_high = max(highs) if highs else 0
        # 最低价：所有K线的最低价
        monthly_low = min(lows) if lows else 0
        # 成交量：总和
        monthly_volume = sum(volumes)

        # 计算涨跌幅
        if monthly_open > 0:
            change_pct = (monthly_close - monthly_open) / monthly_open * 100
            amplitude = (monthly_high - monthly_low) / monthly_open * 100
        else:
            change_pct = 0
            amplitude = 0

        # 获取月末日期
        month_start_date = date.fromisoformat(month_start)
        last_day = date(month_start_date.year, month_start_date.month,
                        calendar.monthrange(month_start_date.year, month_start_date.month)[1])

        monthly_data.append({
            "date": month_start,  # 使用月初作为月K日期
            "month_start": month_start,
            "month_end": last_day.isoformat(),
            "open": monthly_open,
            "close": monthly_close,
            "high": monthly_high,
            "low": monthly_low,
            "volume": monthly_volume,
            "change_pct": round(change_pct, 4),
            "amplitude": round(amplitude, 4),
            "days": len(sorted_items)  # 该月包含的交易天数
        })

    return monthly_data


class PeriodAggregationService:
    """周期聚合计算服务类."""

    def aggregate(
        self,
        daily_data: List[Dict[str, Any]],
        period_type: str
    ) -> List[Dict[str, Any]]:
        """聚合日线数据到指定周期.

        Args:
            daily_data: 日线数据列表
            period_type: 目标周期类型

        Returns:
            聚合后的数据列表
        """
        if period_type == PeriodType.DAILY:
            return daily_data
        elif period_type == PeriodType.WEEKLY:
            return aggregate_to_weekly(daily_data)
        elif period_type == PeriodType.MONTHLY:
            return aggregate_to_monthly(daily_data)
        else:
            # 分钟级数据不支持聚合（需要原始数据）
            return daily_data

    def aggregate_with_indicators(
        self,
        daily_data: List[Dict[str, Any]],
        period_type: str,
        ma_periods: List[int] = [5, 10, 20, 60],
        macd_params: Dict[str, int] = {"fast": 12, "slow": 26, "signal": 9}
    ) -> Dict[str, Any]:
        """聚合数据并计算技术指标.

        Args:
            daily_data: 日线数据列表
            period_type: 目标周期类型
            ma_periods: 均线周期列表
            macd_params: MACD参数

        Returns:
            包含聚合数据和技术指标的结果
        """
        from app.services.technical_service import TechnicalService

        # 聚合数据
        aggregated_data = self.aggregate(daily_data, period_type)

        # 聚合数据并计算技术指标
        tech_service = TechnicalService()

        # 计算均线
        ma_data = {}
        closes = [float(item.get("close", 0)) for item in aggregated_data]

        for period in ma_periods:
            key = f"ma{period}"
            ma_values = []
            if len(closes) >= period:
                for i in range(period - 1, len(closes)):
                    ma_value = sum(closes[i - period + 1:i + 1]) / period
                    ma_values.append({"value": round(ma_value, 4)})
            ma_data[key] = ma_values

        # 计算MACD（使用纯数值）
        fast = macd_params.get("fast", 12)
        slow = macd_params.get("slow", 26)
        signal = macd_params.get("signal", 9)

        if len(closes) < slow + signal:
            macd_data = {"dif": [], "dea": [], "macd": []}
        else:
            # 使用公共EMA函数计算MACD
            ema_fast = calculate_ema(closes, fast)
            ema_slow = calculate_ema(closes, slow)

            dif_values = []
            for i in range(slow - 1, len(ema_fast)):
                dif = ema_fast[i] - ema_slow[i - (slow - fast)]
                dif_values.append(round(dif, 4))

            if len(dif_values) < signal:
                macd_data = {"dif": dif_values, "dea": [], "macd": []}
            else:
                dea_values = calculate_ema(dif_values, signal)
                macd_values = []
                for i in range(len(dea_values)):
                    macd = dif_values[i + signal - 1] - dea_values[i]
                    macd_values.append(round(macd, 4))
                dif_result = dif_values[signal - 1:] if len(dif_values) >= signal else []
                macd_data = {
                    "dif": dif_result,
                    "dea": [round(v, 4) for v in dea_values],
                    "macd": macd_values
                }

        return {
            "data": aggregated_data,
            "ma": ma_data,
            "macd": macd_data,
            "period_type": period_type
        }