"""宏观数据模型测试."""

import pytest
from datetime import date, datetime, timezone
from uuid import UUID

from app.models.macro_config import MacroDataSourceConfig
from app.models.macro_data import MacroDataPoint
from app.models.macro_log import MacroCollectionLog


class TestMacroConfigModel:
    """MacroDataSourceConfig 模型测试."""

    def test_create_config(self, db_session):
        config = MacroDataSourceConfig(
            name="测试数据源",
            source_code="test-source",
            source_type="html",
            url="https://example.com/data",
            parse_engine="beautifulsoup",
            parse_config={"columns": {"date": "Date"}},
        )
        assert config.name == "测试数据源"
        assert config.source_code == "test-source"
        assert config.parse_config == {"columns": {"date": "Date"}}

    def test_default_values(self):
        config = MacroDataSourceConfig(
            name="defaults",
            source_code="def-1",
            source_type="csv",
            url="https://example.com",
            parse_engine="pandas",
            parse_config={},
            retry_max_attempts=3,
            retry_backoff_factor=2.0,
            is_enabled=True,
        )
        assert config.parse_engine == "pandas"
        assert config.parse_config == {}
        assert config.retry_max_attempts == 3
        assert config.retry_backoff_factor == 2.0
        assert config.is_enabled is True


class TestMacroDataPointModel:
    """MacroDataPoint 模型测试."""

    def test_create_data_point(self):
        dp = MacroDataPoint(
            id=UUID("12345678-1234-5678-1234-567812345678"),
            config_id=UUID("12345678-1234-5678-1234-567812345678"),
            source_code="r-star-LW",
            country="US",
            series_name="LW US Natural Rate",
            indicator_key="r_star_lw",
            value=1.25,
            publish_date=date(2023, 3, 31),
            period_date=date(2023, 3, 31),
            frequency="quarterly",
        )
        assert dp.source_code == "r-star-LW"
        assert dp.value == 1.25
        assert dp.frequency == "quarterly"


class TestMacroCollectionLogModel:
    """MacroCollectionLog 模型测试."""

    def test_create_log(self):
        run_time = datetime.now(timezone.utc)
        log = MacroCollectionLog(
            config_id=UUID("12345678-1234-5678-1234-567812345678"),
            run_at=run_time,
            status="success",
            records_count=10,
            is_full=False,
        )
        assert log.status == "success"
        assert log.records_count == 10
        assert log.is_full is False
