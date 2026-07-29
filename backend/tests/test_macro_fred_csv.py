"""FRED CSV 采集器测试."""

import pytest
import uuid

from app.collectors.macro_fred_csv import MacroFREDCSVCollector


@pytest.fixture
def gdp_config():
    return {
        "id": uuid.uuid4(),
        "source_code": "real_gdp",
        "source_type": "csv",
        "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=GDPC1",
        "parse_config": {
            "sid": "GDPC1", "date_col": "observation_date", "value_col": "GDPC1",
            "frequency": "quarterly", "unit": "Billions of Chained 2017 Dollars",
            "indicator_key": "real_gdp",
            "url_template": "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}",
        },
        "timeout_seconds": 30,
        "retry_max_attempts": 2,
        "headers": {},
    }


CSV_DATA = b"""observation_date,GDPC1
1947-01-01,2182.681
1947-04-01,2176.892
2026-01-01,24180.419"""


class TestFREDCSV:
    """FRED CSV 采集器测试."""

    async def test_parse_csv(self, gdp_config):
        collector = MacroFREDCSVCollector(gdp_config)
        df = await collector.parse_raw(CSV_DATA)
        assert len(df) == 3
        assert df.iloc[0]["value"] == 2182.681
        assert df.iloc[0]["period_date"] == "1947-01-01"

    async def test_parse_pce_config(self):
        """core_pce 配置测试."""
        config = {
            "id": uuid.uuid4(),
            "source_code": "core_pce",
            "source_type": "csv",
            "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=PCEPILFE",
            "parse_config": {
                "sid": "PCEPILFE", "date_col": "observation_date", "value_col": "PCEPILFE",
                "frequency": "monthly", "unit": "Index 2017=100",
                "indicator_key": "core_pce",
                "url_template": "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}",
            },
            "timeout_seconds": 30, "retry_max_attempts": 2, "headers": {},
        }
        collector = MacroFREDCSVCollector(config)
        csv = b"observation_date,PCEPILFE\n2026-05-01,130.082"
        df = await collector.parse_raw(csv)
        assert len(df) == 1
        assert df.iloc[0]["frequency"] == "monthly"
        assert df.iloc[0]["unit"] == "Index 2017=100"

    async def test_column_mapping(self, gdp_config):
        """验证列映射正确."""
        collector = MacroFREDCSVCollector(gdp_config)
        df = await collector.parse_raw(CSV_DATA)
        assert "country" in df.columns
        assert df.iloc[0]["country"] == "US"
        assert df.iloc[0]["indicator_key"] == "real_gdp"
