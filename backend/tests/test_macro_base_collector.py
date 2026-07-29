"""宏观数据采集器基类测试."""

import hashlib
import json
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from app.collectors.macro_base_collector import MacroBaseCollector


class _TestCollector(MacroBaseCollector):
    """测试用具体采集器."""

    async def parse_raw(self, raw_data):
        df = pd.DataFrame([
            {
                "country": "US",
                "series_name": "Test R-star",
                "indicator_key": "test_r_star",
                "value": 1.5,
                "publish_date": date(2023, 6, 30),
                "period_date": date(2023, 6, 30),
                "frequency": "quarterly",
            }
        ])
        return df


@pytest.fixture
def test_config():
    return {
        "id": "12345678-1234-5678-1234-567812345678",
        "source_code": "test-source",
        "source_type": "excel",
        "url": "https://example.com/test.xlsx",
        "parse_config": {},
        "headers": {"User-Agent": "FDAS/2.0"},
        "timeout_seconds": 30,
        "retry_max_attempts": 2,
        "retry_backoff_factor": 1.0,
    }


@pytest.fixture
def collector(test_config):
    return _TestCollector(test_config)


class TestHashRow:
    """行哈希测试."""

    def test_hash_deterministic(self, collector):
        """相同输入产生相同哈希."""
        row1 = {"indicator_key": "r1", "period_date": "2023-01-01", "publish_date": "2023-01-05", "value": 1.0, "country": "US"}
        row2 = {"indicator_key": "r1", "period_date": "2023-01-01", "publish_date": "2023-01-05", "value": 1.0, "country": "US"}
        assert collector._hash_row(row1) == collector._hash_row(row2)

    def test_hash_different(self, collector):
        """不同输入产生不同哈希."""
        row1 = {"indicator_key": "r1", "period_date": "2023-01-01", "publish_date": "2023-01-05", "value": 1.0, "country": "US"}
        row2 = {"indicator_key": "r1", "period_date": "2023-01-01", "publish_date": "2023-01-05", "value": 2.0, "country": "US"}
        assert collector._hash_row(row1) != collector._hash_row(row2)


class TestStandardize:
    """数据标准化测试."""

    def test_output_format(self, collector):
        df = pd.DataFrame([{
            "country": "US",
            "series_name": "Test",
            "indicator_key": "test_r",
            "value": 2.0,
            "publish_date": date(2023, 3, 31),
            "period_date": date(2023, 3, 31),
            "frequency": "quarterly",
        }])
        records = collector._standardize(df)
        assert len(records) == 1
        r = records[0]
        assert r["source_code"] == "test-source"
        assert r["country"] == "US"
        assert r["value"] == 2.0
        assert r["publish_date"] == date(2023, 3, 31)
        assert "raw_source_hash" in r
        assert len(r["raw_source_hash"]) == 64

    def test_handles_nan_value(self, collector):
        df = pd.DataFrame([{
            "country": "US",
            "series_name": "Test",
            "indicator_key": "test_r",
            "value": float("nan"),
            "publish_date": date(2023, 3, 31),
            "period_date": None,
            "frequency": "quarterly",
        }])
        records = collector._standardize(df)
        assert len(records) == 1
        assert records[0]["value"] is None


class TestSafeFloat:
    """安全类型转换测试."""

    def test_safe_float(self, collector):
        assert collector._safe_float("1.5") == 1.5
        assert collector._safe_float(3) == 3.0
        assert collector._safe_float(None) is None
        assert collector._safe_float(float("nan")) is None
        assert collector._safe_float("not_a_number") is None


class TestToDate:
    """日期转换测试."""

    def test_to_date(self, collector):
        assert collector._to_date(date(2024, 1, 1)) == date(2024, 1, 1)
        assert collector._to_date("2024-06-15") == date(2024, 6, 15)
        assert collector._to_date(None) is None


class TestIncrementalFilter:
    """增量过滤测试."""

    @patch.object(_TestCollector, "_fetch_raw", new_callable=AsyncMock)
    async def test_full_collect(self, mock_fetch, collector):
        """全量采集不过滤."""
        mock_fetch.return_value = b"fake_data"
        records = await collector.collect(last_publish_date=None)
        assert len(records) == 1
        assert records[0]["publish_date"] == date(2023, 6, 30)

    @patch.object(_TestCollector, "_fetch_raw", new_callable=AsyncMock)
    async def test_incremental_filter(self, mock_fetch, collector):
        """增量采集过滤旧数据."""
        mock_fetch.return_value = b"fake_data"
        # 使用一个较早的日期作为截止点
        records = await collector.collect(last_publish_date=date(2020, 1, 1))
        assert len(records) == 1  # 2023 > 2020, 保留

    @patch.object(_TestCollector, "_fetch_raw", new_callable=AsyncMock)
    async def test_incremental_filter_excludes_old(self, mock_fetch, collector):
        """增量采集排除旧数据."""
        mock_fetch.return_value = b"fake_data"
        # 使用一个较晚的日期作为截止点
        records = await collector.collect(last_publish_date=date(2024, 1, 1))
        assert len(records) == 0  # 2023-06 < 2024-01, 排除
