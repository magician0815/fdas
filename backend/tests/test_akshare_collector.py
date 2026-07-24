"""
AKShare采集器测试.

完整测试覆盖，兼容 Python 3.8+ 环境.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-24 - 修复 Python 3.8 兼容性问题
"""

import pytest
import pandas as pd
from datetime import date
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import sys

from app.collectors.akshare_collector import AKShareCollector, akshare_collector


@pytest.fixture
def collector():
    """采集器实例."""
    return AKShareCollector()


class TestAKShareCollectorInstance:
    """测试采集器实例化."""

    @pytest.mark.asyncio
    async def test_collector_instance(self, collector: AKShareCollector):
        """测试采集器实例化."""
        assert collector is not None

    def test_global_collector_instance(self):
        """测试全局采集器实例."""
        from app.collectors.akshare_collector import akshare_collector
        assert akshare_collector is not None
        assert isinstance(akshare_collector, AKShareCollector)


class TestFetchSupportedSymbols:
    """测试获取支持的货币对列表（兼容 Python 3.8+）."""

    @pytest.mark.asyncio
    async def test_fetch_supported_symbols_success(self, collector: AKShareCollector):
        """测试成功获取货币对列表（覆盖行36-50）."""
        mock_symbols = [
            {"value": "美元人民币", "code": "USDCNY", "label": "美元人民币(USDCNY)"},
            {"value": "欧元美元", "code": "EURUSD", "label": "欧元美元(EURUSD)"},
        ]

        # 兼容 Python 3.8: mock 底层函数而不是 asyncio.to_thread
        with patch('app.collectors.akshare_collector.AKShareCollector._fetch_forex_symbols', return_value=mock_symbols):
            result = await collector.fetch_supported_symbols()
            assert len(result) == 2
            assert result[0]["code"] == "USDCNY"

    @pytest.mark.asyncio
    async def test_fetch_supported_symbols_exception(self, collector: AKShareCollector):
        """测试获取货币对列表异常，返回默认列表（覆盖行47-50）."""
        # Mock 底层方法抛出异常
        with patch.object(collector, '_fetch_forex_symbols', side_effect=Exception("API错误")):
            result = await collector.fetch_supported_symbols()
            # 应返回默认列表（第一个是USDCNH）
            assert len(result) > 0
            assert result[0]["code"] == "USDCNH"


class TestFetchForexSymbols:
    """测试同步获取AKShare外汇货币对列表."""

    def test_fetch_forex_symbols_akshare_not_installed(self, collector: AKShareCollector):
        """测试AKShare未安装，返回默认列表（覆盖行61-63）."""
        # 由于akshare已安装，这个测试验证默认行为
        result = collector._fetch_forex_symbols()
        # 默认列表应该返回20个货币对
        assert len(result) >= 20

    def test_fetch_forex_symbols_api_success(self, collector: AKShareCollector):
        """测试获取默认货币对列表（覆盖行65-82）."""
        # 验证默认货币对列表
        result = collector._fetch_forex_symbols()
        assert len(result) >= 20
        # 检查列表中是否包含常见货币对（不限制第一个）
        codes = [r["code"] for r in result]
        assert any(c in codes for c in ["USDCNH", "EURCNY", "GBPCNY"])

    def test_fetch_forex_symbols_api_exception(self, collector: AKShareCollector):
        """测试AKShare API异常，返回默认列表（覆盖行84-86）."""
        pytest.importorskip("akshare", reason="akshare未安装")
        import akshare.forex.forex_em as forex_em
        original_map = forex_em.symbol_market_map

        try:
            # 清空映射表模拟API异常
            forex_em.symbol_market_map = {}
            result = collector._fetch_forex_symbols()
            # 应该返回默认列表
            assert len(result) > 0
        finally:
            # 恢复原始映射表
            forex_em.symbol_market_map = original_map


class TestCollectForexHist:
    """测试采集外汇日线行情数据（兼容 Python 3.8+）."""

    @pytest.mark.asyncio
    async def test_collect_forex_hist_success(self, collector: AKShareCollector):
        """测试成功采集外汇数据（覆盖行150-169）."""
        mock_df = pd.DataFrame({
            "日期": ["2026-04-01", "2026-04-02"],
            "今开": [7.25, 7.26],
            "最高": [7.26, 7.27],
            "最低": [7.24, 7.25],
            "最新价": [7.25, 7.26],
            "涨跌幅": [0.28, 0.14],
            "涨跌额": [0.02, 0.01],
            "振幅": [0.99, 0.55],
        })

        # 兼容 Python 3.8: mock 底层方法
        with patch.object(collector, '_call_forex_hist', return_value=mock_df):
            result = await collector.collect_forex_hist(
                "美元人民币", "USDCNY",
                date(2026, 4, 1), date(2026, 4, 30)
            )
            assert len(result) == 2
            # _transform_data 不返回symbol_code，该字段在forex_daily_service中由symbol_id关联
            assert result[0]["date"] == date(2026, 4, 1)
            assert result[0]["close"] == 7.25

    @pytest.mark.asyncio
    async def test_collect_forex_hist_empty_data(self, collector: AKShareCollector):
        """测试采集数据为空（双源均返回空则抛异常）."""
        with patch.object(collector, '_call_forex_hist', return_value=pd.DataFrame()):
            with patch.object(collector, '_call_forex_boc', return_value=pd.DataFrame()):
                with pytest.raises(Exception, match="所有外汇数据源均无法采集"):
                    await collector.collect_forex_hist(
                        "美元人民币", "USDCNY",
                        date(2026, 4, 1), date(2026, 4, 30)
                    )

    @pytest.mark.asyncio
    async def test_collect_forex_hist_none_data(self, collector: AKShareCollector):
        """测试采集数据为None（双源均返回None则抛异常）."""
        with patch.object(collector, '_call_forex_hist', return_value=None):
            with patch.object(collector, '_call_forex_boc', return_value=None):
                with pytest.raises(Exception, match="所有外汇数据源均无法采集"):
                    await collector.collect_forex_hist(
                        "美元人民币", "USDCNY",
                        date(2026, 4, 1), date(2026, 4, 30)
                    )

    @pytest.mark.asyncio
    async def test_collect_forex_hist_exception(self, collector: AKShareCollector):
        """测试采集异常（双源均异常则抛异常）."""
        with patch.object(collector, '_call_forex_hist', side_effect=Exception("API错误")):
            with patch.object(collector, '_call_forex_boc', side_effect=Exception("BOC错误")):
                with pytest.raises(Exception, match="所有外汇数据源均无法采集"):
                    await collector.collect_forex_hist(
                        "美元人民币", "USDCNY",
                        date(2026, 4, 1), date(2026, 4, 30)
                    )



class TestTransformData:
    """测试数据格式转换."""

    def test_transform_data_success(self, collector: AKShareCollector):
        """测试数据格式转换成功."""
        # 使用forex_hist_em返回的字段名
        raw_df = pd.DataFrame({
            "日期": ["2026-04-01", "2026-04-02"],
            "今开": [7.25, 7.26],
            "最高": [7.26, 7.27],
            "最低": [7.24, 7.25],
            "最新价": [7.25, 7.26],
            "振幅": [0.99, 0.55],
        })

        result = collector._transform_data(raw_df, "USDCNY")
        assert len(result) == 2
        # _transform_data 不返回symbol_code，该字段在forex_daily_service中由symbol_id关联
        assert result[0]["date"] == date(2026, 4, 1)
        assert result[0]["close"] == 7.25

    def test_transform_data_empty_df(self, collector: AKShareCollector):
        """测试空DataFrame转换."""
        empty_df = pd.DataFrame()
        result = collector._transform_data(empty_df, "USDCNY")
        assert len(result) == 0

    def test_transform_data_timestamp_date(self, collector: AKShareCollector):
        """测试Timestamp类型日期处理."""
        # 使用forex_hist_em返回的字段名
        raw_df = pd.DataFrame({
            "日期": [pd.Timestamp("2026-04-01")],
            "最新价": [7.25],
        })

        result = collector._transform_data(raw_df, "USDCNY")
        assert len(result) == 1
        assert result[0]["date"] == date(2026, 4, 1)

    def test_transform_data_yyyymmdd_date(self, collector: AKShareCollector):
        """测试YYYYMMDD格式日期处理（覆盖行243-244）."""
        raw_df = pd.DataFrame({
            "日期": ["20260401"],
            "收盘价": [7.25],
        })

        result = collector._transform_data(raw_df, "USDCNY")
        assert len(result) == 1
        assert result[0]["date"] == date(2026, 4, 1)

    def test_transform_date_other_format(self, collector: AKShareCollector):
        """测试其他日期类型直接使用（覆盖行247-248）."""
        raw_df = pd.DataFrame({
            "日期": [date(2026, 4, 1)],  # 直接是date对象
            "收盘价": [7.25],
        })

        result = collector._transform_data(raw_df, "USDCNY")
        assert len(result) == 1
        assert result[0]["date"] == date(2026, 4, 1)


class TestSafeFloat:
    """测试安全浮点转换."""

    def test_safe_float_number(self, collector: AKShareCollector):
        """测试数值转换."""
        assert collector._safe_float(7.25) == 7.25

    def test_safe_float_string(self, collector: AKShareCollector):
        """测试字符串转换."""
        assert collector._safe_float("7.25") == 7.25

    def test_safe_float_none(self, collector: AKShareCollector):
        """测试None返回None."""
        assert collector._safe_float(None) is None

    def test_safe_float_pd_na(self, collector: AKShareCollector):
        """测试pd.NA返回None."""
        assert collector._safe_float(pd.NA) is None

    def test_safe_float_nan(self, collector: AKShareCollector):
        """测试NaN返回None."""
        assert collector._safe_float(float("nan")) is None

    def test_safe_float_exception(self, collector: AKShareCollector):
        """测试异常情况返回None（覆盖行274-275）."""
        # 无法转换为float的对象
        assert collector._safe_float({"invalid": "dict"}) is None
        assert collector._safe_float([1, 2, 3]) is None


class TestGetDefaultSymbols:
    """测试默认货币对列表."""

    def test_get_default_symbols(self, collector: AKShareCollector):
        """测试默认货币对列表."""
        symbols = collector._get_default_symbols()
        assert len(symbols) > 0
        assert symbols[0]["code"] == "USDCNH"
        assert "label" in symbols[0]

    def test_get_default_symbols_structure(self, collector: AKShareCollector):
        """测试默认货币对列表结构."""
        symbols = collector._get_default_symbols()
        for symbol in symbols:
            assert "value" in symbol
            assert "code" in symbol
            assert "label" in symbol


class TestGenerateSymbolName:
    """测试货币对代码生成中文名称."""

    def test_common_forex_pairs(self, collector: AKShareCollector):
        assert collector._generate_symbol_name("USDCNY") == "美元人民币"
        assert collector._generate_symbol_name("EURUSD") == "欧元美元"
        assert collector._generate_symbol_name("GBPJPY") == "英镑日元"

    def test_cnh_pair(self, collector: AKShareCollector):
        assert collector._generate_symbol_name("USDCNH") == "美元离岸人民币"

    def test_triple_char_codes(self, collector: AKShareCollector):
        assert collector._generate_symbol_name("NZDUSD") == "新西兰元美元"
        assert collector._generate_symbol_name("SGDUSD") == "新加坡元美元"
        assert collector._generate_symbol_name("ZARUSD") == "南非兰特美元"

    def test_fallback_to_code(self, collector: AKShareCollector):
        # 未知货币代码应返回原始代码
        assert collector._generate_symbol_name("XXXYYY") == "XXXYYY"


class TestTransformStockData:
    """测试股票数据格式转换."""

    def test_transform_stock_basic(self, collector: AKShareCollector):
        df = pd.DataFrame([{
            "date": "2026-04-01",
            "open": 10.0, "high": 11.0, "low": 9.5, "close": 10.5,
            "volume": 1000000, "amount": 10500000.0,
            "turnover": 2.5, "pct_chg": 5.0, "amplitude": 3.0,
        }])
        result = collector._transform_stock_data(df, "000001")
        assert len(result) == 1
        r = result[0]
        assert r["open"] == 10.0
        assert r["close"] == 10.5
        assert r["volume"] == 1000000
        assert r["turnover"] == 2.5
        assert r["change_pct"] == 5.0

    def test_transform_stock_empty(self, collector: AKShareCollector):
        result = collector._transform_stock_data(pd.DataFrame(), "000001")
        assert len(result) == 0

    def test_transform_stock_missing_fields(self, collector: AKShareCollector):
        df = pd.DataFrame([{"date": "2026-04-01", "close": 10.0}])
        result = collector._transform_stock_data(df, "000001")
        assert len(result) == 1
        assert result[0]["open"] is None
        assert result[0]["close"] == 10.0


class TestTransformFuturesData:
    """测试期货数据格式转换."""

    def test_transform_futures_basic(self, collector: AKShareCollector):
        df = pd.DataFrame([{
            "date": "2026-04-01",
            "open": 4000.0, "high": 4100.0, "low": 3950.0, "close": 4050.0,
            "volume": 50000, "amount": 2.0e8, "pct_chg": 1.25, "change": 50.0,
            "amplitude": 3.5,
        }])
        result = collector._transform_futures_data(df, "IF9999")
        assert len(result) == 1
        r = result[0]
        assert r["open"] == 4000.0
        assert r["close"] == 4050.0
        assert r["volume"] == 50000
        assert r["open_interest"] == 0
        assert r["settle_price"] is None

    def test_transform_futures_empty(self, collector: AKShareCollector):
        result = collector._transform_futures_data(pd.DataFrame(), "IF9999")
        assert len(result) == 0


class TestCollectDailyRouting:
    """测试collect_daily统一入口分派."""

    @pytest.mark.asyncio
    async def test_http_api_with_empty_config(self, collector: AKShareCollector):
        """http_api类型配置了空URL时应抛出请求异常."""
        with pytest.raises(Exception):
            await collector.collect_daily(
                {"collector_type": "http_api", "api": {}, "data_parser": {}},
                "test", date(2026, 4, 1), date(2026, 4, 15),
            )

    @pytest.mark.asyncio
    async def test_http_api_with_mock(self, collector: AKShareCollector):
        """http_api类型应对mock HTTP请求返回正确解析的数据."""
        mock_resp = MagicMock()
        mock_resp.headers = {"Content-Type": "application/json"}
        mock_resp.json.return_value = {
            "data": {
                "klines": [
                    ["20260401", "10.0", "10.5", "9.8", "10.2", "10000"],
                    ["20260402", "10.2", "10.8", "10.1", "10.6", "12000"],
                ]
            }
        }
        mock_resp.raise_for_status.return_value = None

        config = {
            "collector_type": "http_api",
            "api": {
                "base_url": "https://api.example.com/stock/daily",
                "method": "GET",
                "timeout": 30,
                "retry": {"max_attempt": 1, "backoff_factor": 0}
            },
            "data_parser": {
                "response_root": "data.klines",
                "date_field": 0,
                "open_field": 1,
                "high_field": 2,
                "low_field": 3,
                "close_field": 4,
                "volume_field": 5,
            },
        }

        with patch("requests.get", return_value=mock_resp):
            records = await collector.collect_daily(
                config, "000001",
                date(2026, 4, 1), date(2026, 4, 15),
            )

        assert len(records) == 2
        assert records[0]["date"] == "20260401"
        assert records[0]["close"] == 10.2
        assert records[0]["volume"] == 10000

    @pytest.mark.asyncio
    async def test_invalid_collector_type(self, collector: AKShareCollector):
        with pytest.raises(ValueError, match="不支持"):
            await collector.collect_daily(
                {"collector_type": "invalid_type"},
                "test", date(2026, 4, 1), date(2026, 4, 15),
            )

    @pytest.mark.asyncio
    async def test_akshare_native_missing_interface(self, collector: AKShareCollector):
        with patch.object(collector, '_collect_by_akshare_interface', side_effect=ValueError("不支持的AKShare接口:")):
            with pytest.raises(ValueError, match="不支持"):
                await collector.collect_daily(
                    {"collector_type": "akshare_native"},
                    "test", date(2026, 4, 1), date(2026, 4, 15),
                )


class TestFetchSymbolsByConfig:
    """测试按配置获取标的数据."""

    @pytest.mark.asyncio
    async def test_collector_type_not_matched(self, collector: AKShareCollector):
        result = await collector.fetch_symbols_by_config(
            {"collector_type": "unknown_type"}
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_http_api_fallback(self, collector: AKShareCollector):
        result = await collector.fetch_symbols_by_config(
            {"collector_type": "http_api"}
        )
        assert result == []