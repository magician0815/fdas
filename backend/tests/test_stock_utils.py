"""
Stock Utils 测试.

测试股票市场识别、涨跌停计算等纯函数.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from app.utils.stock_utils import (
    identify_market_type,
    get_market_config,
    calculate_limit_price,
    is_limit_price,
)


class TestIdentifyMarketType:
    """测试市场类型识别."""

    def test_identify_forex_six_letter_code(self):
        """测试外汇品种识别（6字母代码）."""
        assert identify_market_type("EURUSD") == "forex"
        assert identify_market_type("USDCNY") == "forex"
        assert identify_market_type("GBPJPY") == "forex"

    def test_identify_stock_a_shanghai(self):
        """测试A股沪市识别（6开头）."""
        assert identify_market_type("600000") == "stock_a"
        assert identify_market_type("601398") == "stock_a"

    def test_identify_stock_a_shenzhen(self):
        """测试A股深市识别（0开头）."""
        assert identify_market_type("000001") == "stock_a"
        assert identify_market_type("002415") == "stock_a"

    def test_identify_stock_kcb(self):
        """测试科创板识别（688开头）."""
        assert identify_market_type("688001") == "stock_kcb"
        assert identify_market_type("688111") == "stock_kcb"

    def test_identify_stock_cyb(self):
        """测试创业板识别（300开头）."""
        assert identify_market_type("300001") == "stock_cyb"
        assert identify_market_type("300750") == "stock_cyb"

    def test_identify_stock_bjb(self):
        """测试北交所识别（8开头）."""
        assert identify_market_type("830001") == "stock_bjb"
        assert identify_market_type("430001") == "stock_bjb"

    def test_identify_stock_st(self):
        """测试ST股票识别."""
        assert identify_market_type("600000", "ST某某") == "stock_st"
        assert identify_market_type("000001", "*ST某某") == "stock_st"

    def test_identify_empty_code_returns_forex(self):
        """测试空代码返回外汇."""
        assert identify_market_type("") == "forex"
        assert identify_market_type(None) == "forex"

    def test_identify_case_insensitive(self):
        """测试大小写不敏感."""
        assert identify_market_type("eurusd") == "forex"
        assert identify_market_type("EURUSD") == "forex"


class TestGetMarketConfig:
    """测试市场配置获取."""

    def test_get_forex_config(self):
        """测试外汇配置."""
        config = get_market_config("forex")
        assert config["name"] == "外汇"
        assert config["has_limit"] is False
        assert config["is_24h_trading"] is True
        assert config["price_precision"] == 4

    def test_get_stock_a_config(self):
        """测试A股配置."""
        config = get_market_config("stock_a")
        assert config["name"] == "A股"
        assert config["has_limit"] is True
        assert config["limit_up_threshold"] == 10
        assert config["limit_down_threshold"] == 10

    def test_get_stock_kcb_config(self):
        """测试科创板配置."""
        config = get_market_config("stock_kcb")
        assert config["name"] == "科创板"
        assert config["limit_up_threshold"] == 20
        assert config["limit_down_threshold"] == 20

    def test_get_stock_cyb_config(self):
        """测试创业板配置."""
        config = get_market_config("stock_cyb")
        assert config["name"] == "创业板"
        assert config["limit_up_threshold"] == 20
        assert config["limit_down_threshold"] == 20

    def test_get_stock_st_config(self):
        """测试ST股配置."""
        config = get_market_config("stock_st")
        assert config["name"] == "ST股"
        assert config["limit_up_threshold"] == 5
        assert config["limit_down_threshold"] == 5

    def test_get_stock_bjb_config(self):
        """测试北交所配置."""
        config = get_market_config("stock_bjb")
        assert config["name"] == "北交所"
        assert config["limit_up_threshold"] == 30
        assert config["limit_down_threshold"] == 30

    def test_get_unknown_config_returns_forex(self):
        """测试未知类型返回外汇配置."""
        config = get_market_config("unknown")
        assert config["name"] == "外汇"


class TestCalculateLimitPrice:
    """测试涨跌停价格计算."""

    def test_calculate_limit_up_stock_a(self):
        """测试A股涨停价格."""
        price = calculate_limit_price(10.0, "stock_a", "up")
        assert price == 11.0

    def test_calculate_limit_down_stock_a(self):
        """测试A股跌停价格."""
        price = calculate_limit_price(10.0, "stock_a", "down")
        assert price == 9.0

    def test_calculate_limit_up_stock_kcb(self):
        """测试科创板涨停价格."""
        price = calculate_limit_price(50.0, "stock_kcb", "up")
        assert price == 60.0

    def test_calculate_limit_down_stock_kcb(self):
        """测试科创板跌停价格."""
        price = calculate_limit_price(50.0, "stock_kcb", "down")
        assert price == 40.0

    def test_calculate_limit_up_stock_st(self):
        """测试ST股涨停价格."""
        price = calculate_limit_price(5.0, "stock_st", "up")
        assert price == 5.25

    def test_calculate_limit_down_stock_st(self):
        """测试ST股跌停价格."""
        price = calculate_limit_price(5.0, "stock_st", "down")
        assert price == 4.75

    def test_calculate_limit_forex_returns_zero(self):
        """测试外汇无涨跌停."""
        assert calculate_limit_price(7.25, "forex", "up") == 0
        assert calculate_limit_price(7.25, "forex", "down") == 0

    def test_calculate_limit_precision(self):
        """测试价格精度处理."""
        # A股精度2位
        price = calculate_limit_price(15.555, "stock_a", "up")
        expected = round(15.555 * 1.1 * 100) / 100
        assert price == expected


class TestIsLimitPrice:
    """测试涨跌停判断."""

    def test_is_limit_up_true(self):
        """测试涨停判断为True."""
        assert is_limit_price(11.0, 11.0, "stock_a") is True
        assert is_limit_price(60.0, 60.0, "stock_kcb") is True

    def test_is_limit_up_false(self):
        """测试涨停判断为False."""
        assert is_limit_price(10.5, 11.0, "stock_a") is False
        assert is_limit_price(55.0, 60.0, "stock_kcb") is False

    def test_is_limit_with_tolerance(self):
        """测试涨跌停判断允许误差."""
        # 允许0.01%误差
        assert is_limit_price(11.0001, 11.0, "stock_a") is True
        assert is_limit_price(10.9999, 11.0, "stock_a") is True

    def test_is_limit_forex_returns_false(self):
        """测试外汇无涨跌停."""
        assert is_limit_price(7.25, 7.25, "forex") is False

    def test_is_limit_down_true(self):
        """测试跌停判断为True."""
        assert is_limit_price(9.0, 9.0, "stock_a") is True
        assert is_limit_price(4.75, 4.75, "stock_st") is True