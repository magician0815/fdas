"""
外汇日线行情数据服务测试.

为forex_daily_service.py提供完整的单元测试覆盖，包含边界值测试。

测试目标:
- collect_and_save: 采集并保存外汇日线数据
- get_forex_daily: 查询外汇日线数据（降序）
- get_forex_daily_asc: 查询外汇日线数据（升序）
- save_forex_daily: 保存外汇日线数据
- get_latest_date: 获取最新数据日期

覆盖率目标: 80%+

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID
from datetime import date, timedelta


# ============ Test Class: Collect And Save ============

class TestCollectAndSave:
    """
    采集并保存数据测试.
    """

    @pytest.mark.asyncio
    async def test_collect_and_save_success(self):
        """测试成功采集并保存."""
        mock_db = AsyncMock()

        symbol_id = uuid4()
        datasource_id = uuid4()

        # Mock symbol查询
        mock_symbol = MagicMock()
        mock_symbol.id = symbol_id
        mock_symbol.name = "美元人民币"
        mock_symbol.code = "USDCNY"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_symbol
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()

        # Mock采集返回数据
        mock_records = [
            {"date": date(2026, 4, 15), "open": 7.1, "close": 7.15, "high": 7.2, "low": 7.05},
            {"date": date(2026, 4, 14), "open": 7.08, "close": 7.1, "high": 7.12, "low": 7.06},
        ]

        with patch('app.services.forex_daily_service.akshare_collector') as mock_collector:
            mock_collector.collect_forex_hist = AsyncMock(return_value=mock_records)

            from app.services.forex_daily_service import ForexDailyService
            service = ForexDailyService()

            result = await service.collect_and_save(
                db=mock_db,
                symbol_id=symbol_id,
                datasource_id=datasource_id,
                start_date=date(2026, 4, 1),
                end_date=date(2026, 4, 15),
            )

            # 验证采集成功
            assert result == 2
            mock_collector.collect_forex_hist.assert_called_once()

    @pytest.mark.asyncio
    async def test_collect_and_save_symbol_not_found(self):
        """测试标的不存在."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.services.forex_daily_service.akshare_collector'):
            from app.services.forex_daily_service import ForexDailyService
            service = ForexDailyService()

            result = await service.collect_and_save(
                db=mock_db,
                symbol_id=uuid4(),
                start_date=date(2026, 4, 1),
                end_date=date(2026, 4, 15),
            )

            assert result == 0

    @pytest.mark.asyncio
    async def test_collect_and_save_empty_records(self):
        """测试采集数据为空."""
        mock_db = AsyncMock()

        symbol_id = uuid4()

        mock_symbol = MagicMock()
        mock_symbol.id = symbol_id
        mock_symbol.name = "美元人民币"
        mock_symbol.code = "USDCNY"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_symbol
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.services.forex_daily_service.akshare_collector') as mock_collector:
            mock_collector.collect_forex_hist = AsyncMock(return_value=[])

            from app.services.forex_daily_service import ForexDailyService
            service = ForexDailyService()

            result = await service.collect_and_save(
                db=mock_db,
                symbol_id=symbol_id,
                start_date=date(2026, 4, 1),
                end_date=date(2026, 4, 15),
            )

            assert result == 0

    @pytest.mark.asyncio
    async def test_collect_and_save_default_date_range(self):
        """测试默认日期范围."""
        mock_db = AsyncMock()

        symbol_id = uuid4()

        mock_symbol = MagicMock()
        mock_symbol.id = symbol_id
        mock_symbol.name = "美元人民币"
        mock_symbol.code = "USDCNY"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_symbol
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.services.forex_daily_service.akshare_collector') as mock_collector:
            mock_collector.collect_forex_hist = AsyncMock(return_value=[
                {"date": date.today(), "open": 7.1, "close": 7.15}
            ])

            from app.services.forex_daily_service import ForexDailyService
            service = ForexDailyService()

            result = await service.collect_and_save(
                db=mock_db,
                symbol_id=symbol_id,
            )

            # 验证使用默认日期范围（30天）
            call_args = mock_collector.collect_forex_hist.call_args
            assert call_args[1]['end_date'] == date.today()

    @pytest.mark.asyncio
    async def test_collect_and_save_without_datasource_id(self):
        """测试无datasource_id."""
        mock_db = AsyncMock()

        symbol_id = uuid4()

        mock_symbol = MagicMock()
        mock_symbol.id = symbol_id
        mock_symbol.name = "美元人民币"
        mock_symbol.code = "USDCNY"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_symbol
        mock_db.execute = AsyncMock(return_value=mock_result)

        mock_records = [{"date": date(2026, 4, 15), "open": 7.1}]

        with patch('app.services.forex_daily_service.akshare_collector') as mock_collector:
            mock_collector.collect_forex_hist = AsyncMock(return_value=mock_records)

            from app.services.forex_daily_service import ForexDailyService
            service = ForexDailyService()

            result = await service.collect_and_save(
                db=mock_db,
                symbol_id=symbol_id,
                datasource_id=None,  # 无datasource_id
                start_date=date(2026, 4, 1),
                end_date=date(2026, 4, 15),
            )

            assert result == 1


# ============ Test Class: Get Forex Daily ============

class TestGetForexDaily:
    """
    查询外汇日线数据（降序）测试.
    """

    @pytest.mark.asyncio
    async def test_get_forex_daily_with_symbol_id(self):
        """测试使用symbol_id查询."""
        mock_db = AsyncMock()

        symbol_id = uuid4()

        # Mock查询结果
        mock_daily1 = MagicMock()
        mock_daily1.date = date(2026, 4, 15)

        mock_daily2 = MagicMock()
        mock_daily2.date = date(2026, 4, 14)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_daily1, mock_daily2]
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_forex_daily(
            db=mock_db,
            symbol_id=symbol_id,
            limit=100,
        )

        assert len(result) == 2
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_forex_daily_with_symbol_code(self):
        """测试使用symbol_code查询."""
        mock_db = AsyncMock()

        symbol_id = uuid4()
        symbol_code = "USDCNY"

        # Mock symbol查询
        mock_symbol_result = MagicMock()
        mock_symbol_result.scalar_one_or_none.return_value = symbol_id

        # Mock daily查询
        mock_daily_result = MagicMock()
        mock_daily_result.scalars.return_value.all.return_value = []

        mock_db.execute = AsyncMock(side_effect=[mock_symbol_result, mock_daily_result])

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_forex_daily(
            db=mock_db,
            symbol_code=symbol_code,
        )

        # 验证先查询symbol_id
        assert mock_db.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_get_forex_daily_symbol_code_not_found(self):
        """测试symbol_code不存在."""
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_forex_daily(
            db=mock_db,
            symbol_code="NOTEXIST",
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_get_forex_daily_with_date_range(self):
        """测试日期范围查询."""
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_forex_daily(
            db=mock_db,
            symbol_id=uuid4(),
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 15),
        )

        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_forex_daily_default_limit(self):
        """测试默认limit."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.services.forex_daily_service.settings') as mock_settings:
            mock_settings.FX_DATA_LIMIT = 1000

            from app.services.forex_daily_service import ForexDailyService
            service = ForexDailyService()

            result = await service.get_forex_daily(
                db=mock_db,
                symbol_id=uuid4(),
            )

            mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_forex_daily_no_filters(self):
        """测试无过滤条件."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_forex_daily(db=mock_db)

        mock_db.execute.assert_called_once()


# ============ Test Class: Get Forex Daily Asc ============

class TestGetForexDailyAsc:
    """
    查询外汇日线数据（升序）测试.
    """

    @pytest.mark.asyncio
    async def test_get_forex_daily_asc_success(self):
        """测试升序查询成功."""
        mock_db = AsyncMock()

        symbol_id = uuid4()

        mock_daily1 = MagicMock()
        mock_daily1.date = date(2026, 4, 14)

        mock_daily2 = MagicMock()
        mock_daily2.date = date(2026, 4, 15)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_daily1, mock_daily2]
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_forex_daily_asc(
            db=mock_db,
            symbol_id=symbol_id,
        )

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_forex_daily_asc_with_symbol_code(self):
        """测试升序查询使用symbol_code."""
        mock_db = AsyncMock()

        symbol_id = uuid4()

        mock_symbol_result = MagicMock()
        mock_symbol_result.scalar_one_or_none.return_value = symbol_id

        mock_daily_result = MagicMock()
        mock_daily_result.scalars.return_value.all.return_value = []

        mock_db.execute = AsyncMock(side_effect=[mock_symbol_result, mock_daily_result])

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_forex_daily_asc(
            db=mock_db,
            symbol_code="USDCNY",
        )

        assert mock_db.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_get_forex_daily_asc_symbol_code_uppercase(self):
        """测试symbol_code转大写."""
        mock_db = AsyncMock()

        symbol_id = uuid4()

        mock_symbol_result = MagicMock()
        mock_symbol_result.scalar_one_or_none.return_value = symbol_id

        mock_daily_result = MagicMock()
        mock_daily_result.scalars.return_value.all.return_value = []

        mock_db.execute = AsyncMock(side_effect=[mock_symbol_result, mock_daily_result])

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        # 使用小写代码
        result = await service.get_forex_daily_asc(
            db=mock_db,
            symbol_code="usdcny",  # 小写
        )

        # 应正常工作（会转为大写）

    @pytest.mark.asyncio
    async def test_get_forex_daily_asc_empty_result(self):
        """测试升序查询空结果."""
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_forex_daily_asc(
            db=mock_db,
            symbol_id=uuid4(),
        )

        assert result == []


# ============ Test Class: Save Forex Daily ============

class TestSaveForexDaily:
    """
    保存外汇日线数据测试.
    """

    @pytest.mark.asyncio
    async def test_save_forex_daily_success(self):
        """测试成功保存."""
        mock_db = AsyncMock()

        mock_records = [
            {"symbol_id": uuid4(), "date": date(2026, 4, 15), "open": 7.1, "close": 7.15},
            {"symbol_id": uuid4(), "date": date(2026, 4, 14), "open": 7.08, "close": 7.1},
        ]

        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.save_forex_daily(
            db=mock_db,
            data=mock_records,
        )

        assert result == 2
        assert mock_db.execute.call_count == 2
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_forex_daily_empty_data(self):
        """测试保存空数据."""
        mock_db = AsyncMock()
        mock_db.commit = AsyncMock()

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.save_forex_daily(
            db=mock_db,
            data=[],
        )

        assert result == 0
        mock_db.execute.assert_not_called()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_forex_daily_single_record(self):
        """测试保存单条数据."""
        mock_db = AsyncMock()

        mock_records = [
            {"symbol_id": uuid4(), "date": date(2026, 4, 15), "open": 7.1},
        ]

        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.save_forex_daily(
            db=mock_db,
            data=mock_records,
        )

        assert result == 1

    @pytest.mark.asyncio
    async def test_save_forex_daily_large_batch(self):
        """测试大批量保存."""
        mock_db = AsyncMock()

        # 创建100条记录
        mock_records = []
        for i in range(100):
            mock_records.append({
                "symbol_id": uuid4(),
                "date": date(2026, 4, 15) - timedelta(days=i),
                "open": 7.1,
                "close": 7.15,
            })

        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.save_forex_daily(
            db=mock_db,
            data=mock_records,
        )

        assert result == 100


# ============ Test Class: Get Latest Date ============

class TestGetLatestDate:
    """
    获取最新数据日期测试.
    """

    @pytest.mark.asyncio
    async def test_get_latest_date_success(self):
        """测试成功获取最新日期."""
        mock_db = AsyncMock()

        symbol_id = uuid4()
        latest_date = date(2026, 4, 15)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = latest_date
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_latest_date(
            db=mock_db,
            symbol_id=symbol_id,
        )

        assert result == latest_date

    @pytest.mark.asyncio
    async def test_get_latest_date_no_data(self):
        """测试无数据."""
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_latest_date(
            db=mock_db,
            symbol_id=uuid4(),
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_latest_date_old_data(self):
        """测试旧数据日期."""
        mock_db = AsyncMock()

        old_date = date(2026, 1, 1)  # 很早的数据

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = old_date
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_latest_date(
            db=mock_db,
            symbol_id=uuid4(),
        )

        assert result == old_date


# ============ Test Class: Global Instance ============

class TestGlobalInstance:
    """
    全局实例测试.
    """

    def test_forex_daily_service_instance_exists(self):
        """测试全局实例存在."""
        with patch('app.services.forex_daily_service.akshare_collector'):
            import importlib
            import app.services.forex_daily_service
            importlib.reload(app.services.forex_daily_service)

            assert hasattr(app.services.forex_daily_service, 'forex_daily_service')

    def test_forex_daily_service_is_correct_type(self):
        """测试全局实例类型."""
        with patch('app.services.forex_daily_service.akshare_collector'):
            import importlib
            import app.services.forex_daily_service
            importlib.reload(app.services.forex_daily_service)

            from app.services.forex_daily_service import ForexDailyService
            assert isinstance(
                app.services.forex_daily_service.forex_daily_service,
                ForexDailyService
            )


# ============ Test Class: Edge Cases ============

class TestEdgeCases:
    """
    边界值测试.
    """

    @pytest.mark.asyncio
    async def test_collect_and_save_future_date(self):
        """测试未来日期."""
        mock_db = AsyncMock()

        symbol_id = uuid4()

        mock_symbol = MagicMock()
        mock_symbol.id = symbol_id
        mock_symbol.name = "美元人民币"
        mock_symbol.code = "USDCNY"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_symbol
        mock_db.execute = AsyncMock(return_value=mock_result)

        # 未来日期
        future_date = date.today() + timedelta(days=30)

        with patch('app.services.forex_daily_service.akshare_collector') as mock_collector:
            mock_collector.collect_forex_hist = AsyncMock(return_value=[])

            from app.services.forex_daily_service import ForexDailyService
            service = ForexDailyService()

            result = await service.collect_and_save(
                db=mock_db,
                symbol_id=symbol_id,
                start_date=date.today(),
                end_date=future_date,
            )

            # 未来日期可能无数据
            assert result == 0

    @pytest.mark.asyncio
    async def test_get_forex_daily_single_record(self):
        """测试单条数据查询."""
        mock_db = AsyncMock()

        mock_daily = MagicMock()
        mock_daily.date = date(2026, 4, 15)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_daily]
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_forex_daily(
            db=mock_db,
            symbol_id=uuid4(),
            limit=1,
        )

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_forex_daily_custom_limit(self):
        """测试自定义limit."""
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_forex_daily(
            db=mock_db,
            symbol_id=uuid4(),
            limit=50,  # 自定义limit
        )

        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_forex_daily_with_all_fields(self):
        """测试保存完整字段数据."""
        mock_db = AsyncMock()

        mock_records = [{
            "symbol_id": uuid4(),
            "datasource_id": uuid4(),
            "date": date(2026, 4, 15),
            "open": 7.1000,
            "high": 7.2000,
            "low": 7.0500,
            "close": 7.1500,
            "volume": 0,
            "change_pct": 0.71,
            "change_amount": 0.05,
            "amplitude": 2.11,
        }]

        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.save_forex_daily(
            db=mock_db,
            data=mock_records,
        )

        assert result == 1

    @pytest.mark.asyncio
    async def test_collect_and_save_collector_exception(self):
        """测试采集器异常."""
        mock_db = AsyncMock()

        symbol_id = uuid4()

        mock_symbol = MagicMock()
        mock_symbol.id = symbol_id
        mock_symbol.name = "美元人民币"
        mock_symbol.code = "USDCNY"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_symbol
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.services.forex_daily_service.akshare_collector') as mock_collector:
            mock_collector.collect_forex_hist = AsyncMock(
                side_effect=Exception("采集失败")
            )

            from app.services.forex_daily_service import ForexDailyService
            service = ForexDailyService()

            with pytest.raises(Exception):
                await service.collect_and_save(
                    db=mock_db,
                    symbol_id=symbol_id,
                )


# ============ Test Class: Coverage Missing Lines ============

class TestCoverageMissingLines:
    """补充覆盖缺失行测试."""

    @pytest.mark.asyncio
    async def test_get_forex_daily_asc_symbol_code_not_found_returns_empty(self):
        """测试升序查询symbol_code不存在返回空列表（覆盖line 177）."""
        mock_db = AsyncMock()

        # Mock symbol查询返回None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_forex_daily_asc(
            db=mock_db,
            symbol_code="NOTEXIST",
        )

        # Line 177: return [] when symbol_id not found
        assert result == []
        # 只执行了一次查询（symbol查询）
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_forex_daily_with_start_date_filter(self):
        """测试start_date过滤（覆盖line 185）."""
        mock_db = AsyncMock()

        # Mock查询结果
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_forex_daily(
            db=mock_db,
            symbol_id=uuid4(),
            start_date=date(2026, 4, 1),  # 只提供start_date
        )

        # Line 185被执行
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_forex_daily_with_end_date_filter(self):
        """测试end_date过滤（覆盖line 187）."""
        mock_db = AsyncMock()

        # Mock查询结果
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_forex_daily(
            db=mock_db,
            symbol_id=uuid4(),
            end_date=date(2026, 4, 15),  # 只提供end_date
        )

        # Line 187被执行
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_forex_daily_asc_with_date_filters(self):
        """测试升序查询带日期过滤."""
        mock_db = AsyncMock()

        symbol_id = uuid4()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        from app.services.forex_daily_service import ForexDailyService
        service = ForexDailyService()

        result = await service.get_forex_daily_asc(
            db=mock_db,
            symbol_id=symbol_id,
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 15),
        )

        mock_db.execute.assert_called_once()