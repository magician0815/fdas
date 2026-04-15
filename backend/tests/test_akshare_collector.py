"""
AKShare采集器测试.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-15 - 修复方法名和测试数据格式
"""

import pytest
import pandas as pd
from datetime import date

from app.collectors.akshare_collector import AKShareCollector


@pytest.fixture
def collector():
    """采集器实例."""
    return AKShareCollector()


@pytest.mark.asyncio
async def test_collector_instance(collector: AKShareCollector):
    """测试采集器实例化."""
    assert collector is not None


@pytest.mark.asyncio
async def test_transform_data(collector: AKShareCollector):
    """测试数据格式转换（使用私有方法）."""
    # 模拟AKShare返回的DataFrame格式
    raw_df = pd.DataFrame({
        "日期": ["2026-04-01", "2026-04-02"],
        "开盘价": [7.25, 7.26],
        "最高价": [7.26, 7.27],
        "最低价": [7.24, 7.25],
        "收盘价": [7.25, 7.26],
        "涨跌幅": [0.28, 0.14],
        "涨跌额": [0.02, 0.01],
        "振幅": [0.99, 0.55],
    })

    # 使用私有方法测试（需要处理DataFrame）
    result = collector._transform_data(raw_df, "USDCNH")

    assert len(result) == 2
    assert result[0]["symbol_code"] == "USDCNH"
    assert result[0]["date"] == date(2026, 4, 1)
    assert result[0]["close"] == 7.25
    assert result[0]["change_pct"] == 0.28


@pytest.mark.asyncio
async def test_transform_data_empty_df(collector: AKShareCollector):
    """测试空DataFrame转换."""
    empty_df = pd.DataFrame()
    result = collector._transform_data(empty_df, "USDCNH")
    assert len(result) == 0


@pytest.mark.asyncio
async def test_safe_float(collector: AKShareCollector):
    """测试安全浮点转换."""
    assert collector._safe_float(7.25) == 7.25
    assert collector._safe_float("7.25") == 7.25
    assert collector._safe_float(None) is None
    assert collector._safe_float(pd.NA) is None
    assert collector._safe_float(float("nan")) is None


@pytest.mark.asyncio
async def test_get_default_symbols(collector: AKShareCollector):
    """测试默认货币对列表."""
    symbols = collector._get_default_symbols()
    assert len(symbols) > 0
    assert symbols[0]["code"] == "USDCNY"
    assert "label" in symbols[0]