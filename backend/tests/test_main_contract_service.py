"""
Main Contract Service 测试.

测试期货主力合约拼接逻辑.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from datetime import date

from app.services.main_contract_service import MainContractService


@pytest.fixture
def service():
    """服务实例."""
    return MainContractService()


class TestIdentifyMainContract:
    """测试主力合约识别."""

    def test_identify_main_by_oi(self, service: MainContractService):
        """测试按持仓量识别主力合约."""
        contracts_data = [
            {"contract_id": "IF2401", "date": date(2026, 1, 5), "open_interest": 50000},
            {"contract_id": "IF2402", "date": date(2026, 1, 5), "open_interest": 80000},
            {"contract_id": "IF2403", "date": date(2026, 1, 5), "open_interest": 30000},
        ]

        main_contract = service.identify_main_contract(contracts_data, date(2026, 1, 5))
        assert main_contract == "IF2402"

    def test_identify_main_empty_data(self, service: MainContractService):
        """测试空数据返回None."""
        result = service.identify_main_contract([], date(2026, 1, 5))
        assert result is None

    def test_identify_main_no_data_for_date(self, service: MainContractService):
        """测试无指定日期数据返回None."""
        contracts_data = [
            {"contract_id": "IF2401", "date": date(2026, 1, 5), "open_interest": 50000},
        ]

        result = service.identify_main_contract(contracts_data, date(2026, 1, 10))
        assert result is None

    def test_identify_main_zero_oi(self, service: MainContractService):
        """测试持仓量为0返回None."""
        contracts_data = [
            {"contract_id": "IF2401", "date": date(2026, 1, 5), "open_interest": 0},
        ]

        result = service.identify_main_contract(contracts_data, date(2026, 1, 5))
        assert result is None


class TestDetectContractSwitches:
    """测试主力合约切换点检测."""

    def test_detect_single_switch(self, service: MainContractService):
        """测试检测单次切换."""
        contracts_data = [
            # 第一天：IF2401为主力
            {"contract_id": "IF2401", "contract_code": "IF2401", "date": date(2026, 1, 5),
             "open_interest": 80000, "close": 4000},
            {"contract_id": "IF2402", "contract_code": "IF2402", "date": date(2026, 1, 5),
             "open_interest": 50000, "close": 4020},
            # 第二天：IF2402成为主力（切换）
            {"contract_id": "IF2401", "contract_code": "IF2401", "date": date(2026, 1, 6),
             "open_interest": 30000, "close": 4005},
            {"contract_id": "IF2402", "contract_code": "IF2402", "date": date(2026, 1, 6),
             "open_interest": 90000, "close": 4025},
        ]

        switches = service.detect_contract_switches(contracts_data, "IF")
        assert len(switches) == 1
        assert switches[0]["switch_date"] == date(2026, 1, 6)
        assert switches[0]["old_contract_id"] == "IF2401"
        assert switches[0]["new_contract_id"] == "IF2402"

    def test_detect_no_switch(self, service: MainContractService):
        """测试无切换."""
        contracts_data = [
            {"contract_id": "IF2401", "contract_code": "IF2401", "date": date(2026, 1, 5),
             "open_interest": 80000, "close": 4000},
            {"contract_id": "IF2401", "contract_code": "IF2401", "date": date(2026, 1, 6),
             "open_interest": 90000, "close": 4005},
        ]

        switches = service.detect_contract_switches(contracts_data, "IF")
        assert len(switches) == 0

    def test_detect_empty_data(self, service: MainContractService):
        """测试空数据."""
        switches = service.detect_contract_switches([], "IF")
        assert switches == []

    def test_detect_switch_calculates_price_diff(self, service: MainContractService):
        """测试切换点价格差计算."""
        contracts_data = [
            # Day 1: IF2401 is main (OI=80000)
            {"contract_id": "IF2401", "contract_code": "IF2401", "date": date(2026, 1, 5),
             "open_interest": 80000, "close": 4000},
            {"contract_id": "IF2402", "contract_code": "IF2402", "date": date(2026, 1, 5),
             "open_interest": 50000, "close": 4020},
            # Day 2: IF2402 becomes main (switch)
            {"contract_id": "IF2401", "contract_code": "IF2401", "date": date(2026, 1, 6),
             "open_interest": 30000, "close": 4005},
            {"contract_id": "IF2402", "contract_code": "IF2402", "date": date(2026, 1, 6),
             "open_interest": 90000, "close": 4025},
        ]

        switches = service.detect_contract_switches(contracts_data, "IF")
        # Switch happens on day 2 (Jan 6)
        # According to service logic:
        # old_contract_data is from prev_date (Jan 5) - IF2401 close=4000
        # new_contract_data is from current_date (Jan 6) - IF2402 close=4025
        assert len(switches) == 1
        assert switches[0]["old_close"] == 4000.0  # prev_date's old main contract
        assert switches[0]["new_close"] == 4025.0  # switch day's new main contract
        assert switches[0]["price_diff"] == 25.0


class TestCalculateSpreadAdjustment:
    """测试挢月价格调整计算."""

    def test_proportional_adjustment(self, service: MainContractService):
        """测试比例调整."""
        ratio = service.calculate_spread_adjustment(4000, 4020, "proportional")
        assert ratio == 4000 / 4020

    def test_absolute_adjustment(self, service: MainContractService):
        """测试绝对值调整."""
        diff = service.calculate_spread_adjustment(4000, 4020, "absolute")
        assert diff == -20

    def test_zero_price_returns_default(self, service: MainContractService):
        """测试零价格返回默认值."""
        assert service.calculate_spread_adjustment(0, 4020) == 1.0
        assert service.calculate_spread_adjustment(4000, 0) == 1.0

    def test_unknown_method_returns_default(self, service: MainContractService):
        """测试未知方法返回默认值."""
        ratio = service.calculate_spread_adjustment(4000, 4020, "unknown")
        assert ratio == 1.0


class TestGetContractExpiryWarning:
    """测试合约到期预警."""

    def test_get_expiry_warning(self, service: MainContractService):
        """测试获取即将到期合约."""
        contracts = [
            {"id": "IF2401", "contract_code": "IF2401", "contract_name": "IF2401",
             "last_trade_date": date(2026, 1, 20), "is_main_contract": True},
            {"id": "IF2402", "contract_code": "IF2402", "contract_name": "IF2402",
             "last_trade_date": date(2026, 2, 20), "is_main_contract": False},
        ]

        warnings = service.get_contract_expiry_warning(contracts, date(2026, 1, 15), warning_days=5)
        assert len(warnings) == 1
        assert warnings[0]["contract_code"] == "IF2401"
        assert warnings[0]["days_to_expiry"] == 5

    def test_get_no_expiry_warning(self, service: MainContractService):
        """测试无即将到期合约."""
        contracts = [
            {"id": "IF2402", "contract_code": "IF2402", "contract_name": "IF2402",
             "last_trade_date": date(2026, 2, 20), "is_main_contract": True},
        ]

        warnings = service.get_contract_expiry_warning(contracts, date(2026, 1, 15), warning_days=5)
        assert len(warnings) == 0

    def test_get_expiry_warning_sorted(self, service: MainContractService):
        """测试预警按到期天数排序."""
        contracts = [
            {"id": "IF2401", "contract_code": "IF2401", "contract_name": "IF2401",
             "last_trade_date": date(2026, 1, 20), "is_main_contract": True},
            {"id": "IF2402", "contract_code": "IF2402", "contract_name": "IF2402",
             "last_trade_date": date(2026, 1, 18), "is_main_contract": False},
        ]

        warnings = service.get_contract_expiry_warning(contracts, date(2026, 1, 15), warning_days=10)
        assert len(warnings) == 2
        assert warnings[0]["days_to_expiry"] == 3  # IF2402先到期
        assert warnings[1]["days_to_expiry"] == 5


class TestBuildMainContinuousSeries:
    """测试构建主力连续合约序列."""

    def test_build_empty_series(self, service: MainContractService):
        """测试空数据."""
        result = service.build_main_continuous_series([], [])
        assert result == []

    def test_build_series_with_adjustment(self, service: MainContractService):
        """测试构建带价格调整的序列."""
        contracts_data = [
            {"contract_id": "IF2401", "date": date(2026, 1, 5),
             "open_interest": 80000, "open": 4000, "high": 4010, "low": 3990, "close": 4005},
            {"contract_id": "IF2402", "date": date(2026, 1, 5),
             "open_interest": 50000, "open": 4020, "high": 4030, "low": 4010, "close": 4025},
            # 切换日
            {"contract_id": "IF2401", "date": date(2026, 1, 6),
             "open_interest": 30000, "open": 4010, "high": 4020, "low": 4000, "close": 4015},
            {"contract_id": "IF2402", "date": date(2026, 1, 6),
             "open_interest": 90000, "open": 4030, "high": 4040, "low": 4020, "close": 4035},
        ]

        switches = service.detect_contract_switches(contracts_data, "IF")
        result = service.build_main_continuous_series(contracts_data, switches, "price_adjust")

        assert len(result) > 0
        # 验证主力数据标记
        for item in result:
            assert item.get("is_main_data") is True