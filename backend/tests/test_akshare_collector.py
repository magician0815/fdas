"""
AKShare采集器测试.

Author: FDAS Team
Created: 2026-04-03
"""

import pytest
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
    """测试数据格式转换."""
    raw_data = [
        {"date": "2026-04-01", "open": 7.25, "high": 7.26, "low": 7.24, "close": 7.25, "volume": 1000},
        {"date": "2026-04-02", "open": 7.26, "high": 7.27, "low": 7.25, "close": 7.26, "volume": 1200},
    ]

    result = collector.transform_data(raw_data, "USDCNH")

    assert len(result) == 2
    assert result[0]["symbol"] == "USDCNH"
    assert result[0]["date"] == "2026-04-01"
    assert result[0]["close"] == 7.25