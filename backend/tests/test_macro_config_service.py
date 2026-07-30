"""宏观配置管理服务测试."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.macro_config_service import MacroConfigService, COLLECTOR_CLASS_MAP
from app.models.macro_config import MacroDataSourceConfig
from app.collectors.macro_base_collector import MacroBaseCollector


class TestConfigService:
    """配置管理服务测试."""

    def test_config_to_dict(self, db_session):
        """测试 ORM 转字典."""
        config = MacroDataSourceConfig(
            name="测试",
            source_code="r-star-LW",
            source_type="excel",
            url="https://example.com",
            parse_engine="openpyxl",
            parse_config={"sheet_name": "data"},
            headers={"User-Agent": "test"},
        )
        service = MacroConfigService(db_session)
        d = service.config_to_dict(config)
        assert d["name"] == "测试"
        assert d["source_code"] == "r-star-LW"
        assert d["parse_config"] == {"sheet_name": "data"}

    def test_create_collector_valid(self, db_session):
        """测试采集器工厂: 有效代码."""
        config = MacroDataSourceConfig(
            name="LW",
            source_code="r-star-LW",
            source_type="excel",
            url="https://example.com",
            parse_engine="openpyxl",
            parse_config={},
        )
        service = MacroConfigService(db_session)
        collector = service.create_collector(config)
        assert collector is not None
        assert isinstance(collector, MacroBaseCollector)

    def test_create_collector_unknown(self, db_session):
        """测试采集器工厂: 未知代码返回 None."""
        config = MacroDataSourceConfig(
            name="Unknown",
            source_code="unknown-code",
            source_type="excel",
            url="https://example.com",
            parse_engine="openpyxl",
            parse_config={},
        )
        service = MacroConfigService(db_session)
        collector = service.create_collector(config)
        assert collector is None

    def test_collector_class_map_coverage(self):
        """确保所有数据源代码都有对应的采集器."""
        expected = {"r-star-LW", "r-star-HLW", "r-star-LM", "r-sep", "longer-run-neutral",
                    "real_gdp", "potential_gdp", "core_pce"}
        assert expected == set(COLLECTOR_CLASS_MAP.keys())
