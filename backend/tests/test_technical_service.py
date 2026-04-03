"""
技术指标服务测试.

Author: FDAS Team
Created: 2026-04-03
"""

import pytest
from decimal import Decimal

from app.models.fx_data import FXData
from app.services.technical_service import TechnicalService


@pytest.fixture
def technical_service():
    """技术指标服务实例."""
    return TechnicalService()


@pytest.fixture
def sample_fx_data():
    """示例汇率数据."""
    # 创建20条测试数据
    data = []
    for i in range(20):
        fx = FXData(
            symbol="USDCNH",
            date=f"2026-04-{i+1:02d}",
            open=Decimal("7.25") + Decimal(str(i * 0.01)),
            high=Decimal("7.26") + Decimal(str(i * 0.01)),
            low=Decimal("7.24") + Decimal(str(i * 0.01)),
            close=Decimal("7.25") + Decimal(str(i * 0.01)),
            volume=1000,
        )
        data.append(fx)
    return data


def test_technical_service_instance(technical_service: TechnicalService):
    """测试服务实例化."""
    assert technical_service is not None


def test_calculate_ma(technical_service: TechnicalService, sample_fx_data):
    """测试MA计算."""
    result = technical_service.calculate_ma(sample_fx_data, period=5)

    assert result is not None
    assert len(result) > 0
    # MA值应该在合理范围内
    for ma in result:
        assert "value" in ma
        assert ma["value"] > 0