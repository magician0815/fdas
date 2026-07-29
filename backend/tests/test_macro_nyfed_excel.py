"""NY Fed Excel 采集器测试."""

from io import BytesIO
from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest
import openpyxl

from app.collectors.macro_nyfed_excel import MacroNYFedExcelCollector


@pytest.fixture
def lw_config():
    return {
        "id": "12345678-1234-5678-1234-567812345678",
        "source_code": "r-star-LW",
        "source_type": "excel",
        "url": "https://example.com/lw.xlsx",
        "parse_config": {
            "sheet_name": "data",
            "skiprows": 0,
            "frequency": "quarterly",
            "columns": {"date": "Date", "r_star_lw": "r-star"},
            "indicator_key": "r_star_lw",
            "country": "US",
        },
        "timeout_seconds": 30,
        "retry_max_attempts": 2,
    }


@pytest.fixture
def hlw_config():
    return {
        "id": "22345678-1234-5678-1234-567812345678",
        "source_code": "r-star-HLW",
        "source_type": "excel",
        "url": "https://example.com/hlw.xlsx",
        "parse_config": {
            "sheet_name": "data",
            "skiprows": 0,
            "frequency": "quarterly",
            "columns": {"date": "Date", "country": "Country", "r_star_hlw": "r-star"},
            "indicator_key": "r_star_hlw",
            "multi_country": True,
        },
        "timeout_seconds": 30,
        "retry_max_attempts": 2,
    }


def _create_test_excel():
    """创建测试 Excel 文件 (LW 模式)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "data"
    ws.append(["Date", "r-star", "other"])
    ws.append(["2023-03-31", 1.25, "x"])
    ws.append(["2023-06-30", 1.30, "x"])
    ws.append(["2023-09-30", 1.28, "x"])
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _create_test_excel_hlw():
    """创建测试 Excel 文件 (HLW 多国模式)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "data"
    ws.append(["Date", "Country", "r-star"])
    ws.append(["2023-03-31", "US", 1.25])
    ws.append(["2023-06-30", "US", 1.30])
    ws.append(["2023-03-31", "CA", 0.80])
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


class TestNYFedExcelLW:
    """LW 模型 Excel 解析测试."""

    async def test_parse_lw_single_country(self, lw_config):
        collector = MacroNYFedExcelCollector(lw_config)
        raw = _create_test_excel()
        df = await collector.parse_raw(raw)
        assert len(df) == 3
        assert df.iloc[0]["country"] == "US"
        assert df.iloc[0]["indicator_key"] == "r_star_lw"
        assert df.iloc[0]["value"] == 1.25
        assert df.iloc[0]["period_date"] == "2023-03-31"


class TestNYFedExcelHLW:
    """HLW 模型 Excel 解析测试."""

    async def test_parse_hlw_multi_country(self, hlw_config):
        collector = MacroNYFedExcelCollector(hlw_config)
        raw = _create_test_excel_hlw()
        df = await collector.parse_raw(raw)
        assert len(df) == 3
        countries = set(df["country"])
        assert "US" in countries
        assert "CA" in countries
        assert df.iloc[0]["indicator_key"] == "r_star_hlw"
