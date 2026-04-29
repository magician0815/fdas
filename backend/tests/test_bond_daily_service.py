"""
债券日线行情数据服务测试.

测试目标:
- collect_and_save: 标的不存在 / 采集器未实现
- get_bond_daily: 按symbol_id / market_id / 日期范围
- get_bond_daily_asc: 升序查询
- save_bond_daily: 批量保存含ON CONFLICT
- get_latest_date: 有数据 / 无数据

Author: FDAS Team
Created: 2026-04-29
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import date

from app.services.bond_daily_service import BondDailyService


class TestCollectAndSave:
    """collect_and_save 测试."""

    @pytest.mark.asyncio
    async def test_symbol_not_found(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = BondDailyService()
        result = await service.collect_and_save(db=mock_db, symbol_id=uuid4())
        assert result == 0

    @pytest.mark.asyncio
    async def test_collector_not_implemented(self):
        mock_db = AsyncMock()
        mock_symbol = MagicMock()
        mock_symbol.market_id = uuid4()
        mock_symbol.name = "测试债券"
        mock_symbol.code = "010107"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_symbol
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.services.bond_daily_service.AKShareCollector') as MockCollector:
            mock_collector = AsyncMock()
            mock_collector.collect_daily.side_effect = NotImplementedError()
            MockCollector.return_value = mock_collector

            service = BondDailyService()
            result = await service.collect_and_save(db=mock_db, symbol_id=uuid4())
            assert result == 0


class TestGetBondDaily:
    """get_bond_daily 查询测试."""

    @pytest.mark.asyncio
    async def test_with_symbol_id(self):
        mock_db = AsyncMock()
        mock_daily = MagicMock()
        mock_daily.date = date(2026, 4, 15)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_daily]
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = BondDailyService()
        result = await service.get_bond_daily(
            db=mock_db, symbol_id=uuid4(), limit=100)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_with_market_id(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = BondDailyService()
        result = await service.get_bond_daily(db=mock_db, market_id=uuid4())
        assert result == []

    @pytest.mark.asyncio
    async def test_with_date_range(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = BondDailyService()
        result = await service.get_bond_daily(
            db=mock_db,
            symbol_id=uuid4(),
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 15),
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_no_filters(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = BondDailyService()
        result = await service.get_bond_daily(db=mock_db)
        assert result == []

    @pytest.mark.asyncio
    async def test_with_all_filters(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = BondDailyService()
        result = await service.get_bond_daily(
            db=mock_db,
            symbol_id=uuid4(),
            market_id=uuid4(),
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 15),
            limit=50,
        )
        assert result == []


class TestGetBondDailyAsc:
    """get_bond_daily_asc 升序查询测试."""

    @pytest.mark.asyncio
    async def test_asc_order(self):
        mock_db = AsyncMock()
        d1 = MagicMock()
        d1.date = date(2026, 4, 1)
        d2 = MagicMock()
        d2.date = date(2026, 4, 15)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [d1, d2]
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = BondDailyService()
        result = await service.get_bond_daily_asc(
            db=mock_db, symbol_id=uuid4())
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_with_market_and_date(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = BondDailyService()
        result = await service.get_bond_daily_asc(
            db=mock_db,
            symbol_id=uuid4(),
            market_id=uuid4(),
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 15),
        )
        assert result == []


class TestSaveBondDaily:
    """save_bond_daily 保存测试."""

    @pytest.mark.asyncio
    async def test_save_single_record(self):
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()

        service = BondDailyService()
        records = [{
            "symbol_id": uuid4(),
            "market_id": uuid4(),
            "date": date(2026, 4, 15),
            "open": 100.0, "high": 101.0, "low": 99.5, "close": 100.5,
            "yield_rate": 2.85,
        }]
        result = await service.save_bond_daily(mock_db, records)
        assert result == 1
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_multiple_records(self):
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()

        service = BondDailyService()
        records = [
            {"symbol_id": uuid4(), "market_id": uuid4(), "date": date(2026, 4, 14), "open": 100.0},
            {"symbol_id": uuid4(), "market_id": uuid4(), "date": date(2026, 4, 15), "open": 100.5},
        ]
        result = await service.save_bond_daily(mock_db, records)
        assert result == 2
        assert mock_db.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_save_empty_list(self):
        mock_db = AsyncMock()
        service = BondDailyService()
        result = await service.save_bond_daily(mock_db, [])
        assert result == 0


class TestGetLatestDate:
    """get_latest_date 测试."""

    @pytest.mark.asyncio
    async def test_returns_date(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = date(2026, 4, 15)
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = BondDailyService()
        result = await service.get_latest_date(mock_db, uuid4())
        assert result == date(2026, 4, 15)

    @pytest.mark.asyncio
    async def test_no_data_returns_none(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = BondDailyService()
        result = await service.get_latest_date(mock_db, uuid4())
        assert result is None
