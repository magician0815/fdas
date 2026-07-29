"""宏观采集编排服务测试."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from app.services.macro_collection_service import MacroCollectionService
from app.models.macro_config import MacroDataSourceConfig


@pytest.fixture
def collection_service():
    return MacroCollectionService()


async def _setup_collect_mocks(mock_config_svc_cls, mock_session_cls):
    """设置 collect 方法所需的 mocks."""
    mock_db = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.add = MagicMock()
    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_db.execute = AsyncMock(return_value=mock_result)

    # AsyncSessionLocal() 返回异步上下文管理器
    mock_session_ctx = AsyncMock()
    mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_db)
    mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
    mock_session_cls.return_value = mock_session_ctx

    mock_config = MagicMock(spec=MacroDataSourceConfig)
    mock_config.id = UUID("12345678-1234-5678-1234-567812345678")
    mock_config.source_code = "r-star-LW"
    mock_config.name = "test"

    mock_config_svc = AsyncMock()
    mock_config_svc.get_config = AsyncMock(return_value=mock_config)

    mock_collector = AsyncMock()
    mock_collector.collect = AsyncMock(return_value=[])
    mock_config_svc.create_collector = MagicMock(return_value=mock_collector)

    mock_config_svc_cls.return_value = mock_config_svc

    return mock_config_svc, mock_collector, mock_db


class TestCollect:
    """采集执行测试."""

    @patch("app.services.macro_collection_service.MacroConfigService")
    @patch("app.services.macro_collection_service.AsyncSessionLocal")
    async def test_collect_full(self, mock_session_cls, mock_config_svc_cls, collection_service):
        """全量采集流程."""
        _, mock_collector, _ = await _setup_collect_mocks(mock_config_svc_cls, mock_session_cls)

        config_id = UUID("12345678-1234-5678-1234-567812345678")
        await collection_service.collect(config_id, full=True)

        mock_collector.collect.assert_called_once_with(last_publish_date=None)

    @patch("app.services.macro_collection_service.MacroConfigService")
    @patch("app.services.macro_collection_service.AsyncSessionLocal")
    async def test_collect_with_data(self, mock_session_cls, mock_config_svc_cls, collection_service):
        """采集并入库."""
        mock_config_svc, mock_collector, mock_db = await _setup_collect_mocks(
            mock_config_svc_cls, mock_session_cls
        )
        mock_collector.collect = AsyncMock(return_value=[{
            "config_id": UUID("12345678-1234-5678-1234-567812345678"),
            "source_code": "r-star-LW",
            "country": "US",
            "series_name": "Test",
            "indicator_key": "r_star_lw",
            "value": 1.5,
            "publish_date": None,
            "period_date": None,
            "frequency": "quarterly",
            "forecast_year": None,
            "unit": "percent",
            "extra_info": {},
            "raw_source_hash": "abc123",
        }])

        config_id = UUID("12345678-1234-5678-1234-567812345678")
        await collection_service.collect(config_id, full=False)

        assert mock_db.execute.call_count >= 1  # 数据入库


class TestEnableDisable:
    """调度启用/禁用测试."""

    @patch("app.services.macro_collection_service.MacroConfigService")
    @patch("app.services.macro_collection_service.scheduler_service")
    async def test_disable_schedule(self, mock_scheduler, mock_cs_cls, collection_service):
        """禁用调度."""
        mock_db = AsyncMock()
        config_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_config = MagicMock(spec=MacroDataSourceConfig)
        mock_config.id = config_id
        mock_config_svc = AsyncMock()
        mock_config_svc.get_config = AsyncMock(return_value=mock_config)
        mock_cs_cls.return_value = mock_config_svc

        result = await collection_service.disable_schedule(config_id, mock_db)

        assert result is True
        mock_scheduler.remove_job.assert_called_once_with(f"macro-{config_id}")
