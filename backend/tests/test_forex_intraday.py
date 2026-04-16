"""
ForexIntraday模型测试.

测试外汇分钟级行情模型的to_dict方法.

Author: FDAS Team
Created: 2026-04-16
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.models.forex_intraday import ForexIntraday


class TestForexIntradayToDict:
    """测试ForexIntraday.to_dict方法."""

    def test_to_dict_with_id(self):
        """测试有ID时的to_dict转换."""
        model = ForexIntraday(
            id=uuid4(),
            symbol_id=uuid4(),
            datasource_id=uuid4(),
            timestamp=datetime(2026, 4, 1, 10, 30, 0),
            interval="5",
            open=7.25,
            high=7.26,
            low=7.24,
            close=7.255,
            volume=0,
            updated_at=datetime(2026, 4, 1, 10, 35, 0)
        )

        result = model.to_dict()

        assert result["id"] is not None
        assert isinstance(result["id"], str)
        assert result["symbol_id"] is not None
        assert result["datasource_id"] is not None
        assert result["timestamp"] == "2026-04-01T10:30:00"
        assert result["interval"] == "5"
        assert result["open"] == 7.25
        assert result["high"] == 7.26
        assert result["low"] == 7.24
        assert result["close"] == 7.255
        assert result["volume"] == 0

    def test_to_dict_without_id(self):
        """测试ID为None时的to_dict转换（覆盖行63-64）."""
        model = ForexIntraday(
            id=None,  # ID为None
            symbol_id=uuid4(),
            timestamp=datetime(2026, 4, 1, 10, 30, 0),
            interval="1",
            open=7.25,
            high=7.26,
            low=7.24,
            close=7.255,
        )

        result = model.to_dict()

        assert result["id"] is None  # 覆盖行64: id为None时返回None
        assert result["symbol_id"] is not None
        assert result["interval"] == "1"

    def test_to_dict_without_symbol_id(self):
        """测试symbol_id为None时的to_dict转换."""
        model = ForexIntraday(
            id=uuid4(),
            symbol_id=None,
            timestamp=datetime(2026, 4, 1, 10, 30, 0),
            interval="15",
        )

        result = model.to_dict()

        assert result["id"] is not None
        assert result["symbol_id"] is None

    def test_to_dict_without_datasource_id(self):
        """测试datasource_id为None时的to_dict转换."""
        model = ForexIntraday(
            id=uuid4(),
            symbol_id=uuid4(),
            datasource_id=None,  # datasource_id为None
            timestamp=datetime(2026, 4, 1, 10, 30, 0),
            interval="30",
        )

        result = model.to_dict()

        assert result["datasource_id"] is None

    def test_to_dict_without_timestamp(self):
        """测试timestamp为None时的to_dict转换."""
        model = ForexIntraday(
            id=uuid4(),
            symbol_id=uuid4(),
            timestamp=None,
            interval="60",
        )

        result = model.to_dict()

        assert result["timestamp"] is None

    def test_to_dict_without_prices(self):
        """测试价格为None时的to_dict转换."""
        model = ForexIntraday(
            id=uuid4(),
            symbol_id=uuid4(),
            timestamp=datetime(2026, 4, 1, 10, 30, 0),
            interval="5",
            open=None,
            high=None,
            low=None,
            close=None,
        )

        result = model.to_dict()

        assert result["open"] is None
        assert result["high"] is None
        assert result["low"] is None
        assert result["close"] is None

    def test_to_dict_without_updated_at(self):
        """测试updated_at为None时的to_dict转换."""
        model = ForexIntraday(
            id=uuid4(),
            symbol_id=uuid4(),
            timestamp=datetime(2026, 4, 1, 10, 30, 0),
            interval="5",
            updated_at=None,
        )

        result = model.to_dict()

        assert result["updated_at"] is None


class TestForexIntradayFields:
    """测试ForexIntraday字段属性."""

    def test_interval_column_default(self):
        """测试interval列默认值为'1'."""
        # 检查列定义的default值
        from sqlalchemy import inspect
        mapper = inspect(ForexIntraday)
        interval_col = mapper.columns.interval
        # 默认值在数据库层面设置，不是Python实例层面
        assert interval_col.default is not None or interval_col.server_default is not None

    def test_volume_column_default(self):
        """测试volume列默认值为0."""
        from sqlalchemy import inspect
        mapper = inspect(ForexIntraday)
        volume_col = mapper.columns.volume
        assert volume_col.default is not None or volume_col.server_default is not None

    def test_table_name(self):
        """测试表名."""
        assert ForexIntraday.__tablename__ == "forex_intraday"