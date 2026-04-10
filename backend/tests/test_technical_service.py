"""
技术指标服务测试.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-10 - 适配ForexDaily模型
"""

import pytest
from decimal import Decimal
from datetime import date
import uuid

from app.models.forex_daily import ForexDaily
from app.services.technical_service import technical_service


@pytest.fixture
def sample_forex_daily_data():
    """示例外汇日线数据."""
    # 创建20条测试数据（模拟ForexDaily对象）
    data = []
    test_symbol_id = uuid.uuid4()
    test_datasource_id = uuid.uuid4()

    for i in range(20):
        daily = ForexDaily(
            id=uuid.uuid4(),
            symbol_id=test_symbol_id,
            datasource_id=test_datasource_id,
            date=date(2026, 4, i + 1),
            open=Decimal("7.25") + Decimal(str(i * 0.01)),
            high=Decimal("7.26") + Decimal(str(i * 0.01)),
            low=Decimal("7.24") + Decimal(str(i * 0.01)),
            close=Decimal("7.25") + Decimal(str(i * 0.01)),
            change_pct=Decimal("0.28"),
            change_amount=Decimal("0.02"),
            amplitude=Decimal("0.99"),
        )
        data.append(daily)
    return data


def test_technical_service_instance():
    """测试服务实例化."""
    assert technical_service is not None


def test_calculate_ma(sample_forex_daily_data):
    """测试MA计算."""
    result = technical_service.calculate_ma(sample_forex_daily_data, period=5)

    assert result is not None
    assert len(result) > 0
    # MA值应该在合理范围内
    for ma in result:
        assert "value" in ma
        assert ma["value"] > 0


def test_calculate_ma_short_data(sample_forex_daily_data):
    """测试数据不足时的MA计算."""
    # 使用少量数据
    short_data = sample_forex_daily_data[:3]

    # 5周期MA应该返回空结果（数据不足）
    result = technical_service.calculate_ma(short_data, period=5)
    assert result == []


def test_calculate_macd(sample_forex_daily_data):
    """测试MACD计算."""
    result = technical_service.calculate_macd(sample_forex_daily_data)

    assert result is not None
    assert "macd" in result
    assert "signal" in result
    assert "hist" in result


def test_calculate_all_indicators(sample_forex_daily_data):
    """测试所有技术指标计算."""
    result = technical_service.calculate_all_indicators(sample_forex_daily_data)

    assert result is not None
    assert "ma" in result
    assert "macd" in result