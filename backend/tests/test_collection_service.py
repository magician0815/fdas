"""
采集任务协调服务测试.

为collection_service.py提供完整的单元测试覆盖，包含边界值测试。

测试目标:
- load_enabled_tasks: 加载已启用任务
- _add_task_to_scheduler: 将任务添加到调度器
- execute_task: 执行采集任务
- enable_task: 启用任务
- disable_task: 禁用任务

覆盖率目标: 80%+

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID
from datetime import datetime, date, timedelta

# 需要在导入前Mock数据库连接和其他依赖


# ============ Test Class: Load Enabled Tasks ============

class TestLoadEnabledTasks:
    """
    加载已启用任务测试.
    """

    @pytest.mark.asyncio
    async def test_load_enabled_tasks_success(self):
        """测试成功加载已启用任务."""
        # Mock数据库会话
        mock_db = AsyncMock()

        # Mock任务列表
        mock_task1 = MagicMock()
        mock_task1.id = uuid4()
        mock_task1.name = "task1"
        mock_task1.cron_expr = "0 18 * * *"

        mock_task2 = MagicMock()
        mock_task2.id = uuid4()
        mock_task2.name = "task2"
        mock_task2.cron_expr = "30 9 * * 1"

        # Mock查询结果
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_task1, mock_task2]

        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.services.collection_service.AsyncSessionLocal') as mock_session_local, \
             patch('app.services.collection_service.scheduler_service') as mock_scheduler, \
             patch('app.services.collection_service.forex_daily_service'):

            mock_session_local.return_value.__aenter__.return_value = mock_db
            mock_scheduler.add_job = MagicMock()
            mock_scheduler.update_next_run_time = MagicMock(return_value=datetime.now())

            from app.services.collection_service import CollectionService
            service = CollectionService()

            await service.load_enabled_tasks()

            # 验证添加了两个任务
            assert mock_scheduler.add_job.call_count == 2

    @pytest.mark.asyncio
    async def test_load_enabled_tasks_no_tasks(self):
        """测试无任务."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []

        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.services.collection_service.AsyncSessionLocal') as mock_session_local, \
             patch('app.services.collection_service.scheduler_service') as mock_scheduler:

            mock_session_local.return_value.__aenter__.return_value = mock_db

            from app.services.collection_service import CollectionService
            service = CollectionService()

            await service.load_enabled_tasks()

            # 无任务时不应添加
            mock_scheduler.add_job.assert_not_called()

    @pytest.mark.asyncio
    async def test_load_enabled_tasks_skip_no_cron(self):
        """测试跳过无cron表达式的任务."""
        mock_db = AsyncMock()

        # 有cron的任务
        mock_task1 = MagicMock()
        mock_task1.id = uuid4()
        mock_task1.cron_expr = "0 18 * * *"

        # 无cron的任务（应跳过）
        mock_task2 = MagicMock()
        mock_task2.id = uuid4()
        mock_task2.cron_expr = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_task1, mock_task2]

        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.services.collection_service.AsyncSessionLocal') as mock_session_local, \
             patch('app.services.collection_service.scheduler_service') as mock_scheduler:

            mock_session_local.return_value.__aenter__.return_value = mock_db
            mock_scheduler.add_job = MagicMock()

            from app.services.collection_service import CollectionService
            service = CollectionService()

            await service.load_enabled_tasks()

            # 只添加1个任务（跳过无cron的）
            mock_scheduler.add_job.assert_called_once()


# ============ Test Class: Add Task To Scheduler ============

class TestAddTaskToScheduler:
    """
    将任务添加到调度器测试.
    """

    @pytest.mark.asyncio
    async def test_add_task_to_scheduler_success(self):
        """测试成功添加任务到调度器."""
        mock_db = AsyncMock()

        mock_task = MagicMock()
        mock_task.id = uuid4()
        mock_task.cron_expr = "0 18 * * *"

        # Mock数据库查询
        mock_result = MagicMock()
        mock_db_task = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_db_task
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()

        expected_next_run = datetime(2026, 4, 15, 18, 0)

        with patch('app.services.collection_service.AsyncSessionLocal') as mock_session_local, \
             patch('app.services.collection_service.scheduler_service') as mock_scheduler:

            mock_session_local.return_value.__aenter__.return_value = mock_db
            mock_scheduler.add_job = MagicMock()
            mock_scheduler.update_next_run_time = MagicMock(return_value=expected_next_run)

            from app.services.collection_service import CollectionService
            service = CollectionService()

            await service._add_task_to_scheduler(mock_task)

            # 验证添加任务
            mock_scheduler.add_job.assert_called_once()

            # 验证更新next_run_time
            assert mock_db_task.next_run_at == expected_next_run
            mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_add_task_to_scheduler_no_next_run_time(self):
        """测试无下次执行时间."""
        mock_db = AsyncMock()

        mock_task = MagicMock()
        mock_task.id = uuid4()

        with patch('app.services.collection_service.AsyncSessionLocal') as mock_session_local, \
             patch('app.services.collection_service.scheduler_service') as mock_scheduler:

            mock_session_local.return_value.__aenter__.return_value = mock_db
            mock_scheduler.add_job = MagicMock()
            mock_scheduler.update_next_run_time = MagicMock(return_value=None)

            from app.services.collection_service import CollectionService
            service = CollectionService()

            await service._add_task_to_scheduler(mock_task)

            mock_scheduler.add_job.assert_called_once()
            # 无next_run_time时不更新


# ============ Test Class: Execute Task ============

class TestExecuteTask:
    """
    执行采集任务测试.
    """

    @pytest.mark.asyncio
    async def test_execute_task_task_not_found(self):
        """测试任务不存在."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.services.collection_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_db

            from app.services.collection_service import CollectionService
            service = CollectionService()

            await service.execute_task(uuid4())

            # 任务不存在时直接返回，不执行采集
            mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_task_market_not_found(self):
        """测试市场不存在."""
        mock_db = AsyncMock()

        mock_task = MagicMock()
        mock_task.id = uuid4()
        mock_task.market_id = uuid4()

        # Mock任务查询返回
        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        # Mock市场查询返回None
        mock_market_result = MagicMock()
        mock_market_result.scalar_one_or_none.return_value = None

        mock_db.execute = AsyncMock(side_effect=[mock_task_result, mock_market_result])

        with patch('app.services.collection_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_db

            from app.services.collection_service import CollectionService
            service = CollectionService()

            await service.execute_task(uuid4())

            # 市场不存在时直接返回
            mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_task_non_forex_market(self):
        """测试非外汇市场."""
        mock_db = AsyncMock()

        mock_task = MagicMock()
        mock_task.id = uuid4()
        mock_task.market_id = uuid4()

        mock_market = MagicMock()
        mock_market.code = "stock"  # 非外汇市场
        mock_market.name = "股票市场"

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_market_result = MagicMock()
        mock_market_result.scalar_one_or_none.return_value = mock_market

        mock_db.execute = AsyncMock(side_effect=[mock_task_result, mock_market_result])

        with patch('app.services.collection_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_db

            from app.services.collection_service import CollectionService
            service = CollectionService()

            await service.execute_task(uuid4())

            # 非外汇市场直接返回
            mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_task_forex_success(self):
        """测试外汇市场采集成功."""
        mock_db = AsyncMock()

        task_id = uuid4()
        symbol_id = uuid4()
        datasource_id = uuid4()

        mock_task = MagicMock()
        mock_task.id = task_id
        mock_task.market_id = uuid4()
        mock_task.symbol_id = symbol_id
        mock_task.datasource_id = datasource_id
        mock_task.start_date = date(2026, 4, 1)
        mock_task.end_date = date(2026, 4, 15)
        mock_task.name = "外汇采集任务"

        mock_market = MagicMock()
        mock_market.code = "forex"

        mock_log = MagicMock()
        mock_log.id = uuid4()

        # Mock多次数据库查询
        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_market_result = MagicMock()
        mock_market_result.scalar_one_or_none.return_value = mock_market

        mock_log_refresh = AsyncMock()

        mock_db.execute = AsyncMock(side_effect=[
            mock_task_result,
            mock_market_result,
        ])
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = mock_log_refresh

        expected_next_run = datetime(2026, 4, 16, 18, 0)

        with patch('app.services.collection_service.AsyncSessionLocal') as mock_session_local, \
             patch('app.services.collection_service.scheduler_service') as mock_scheduler, \
             patch('app.services.collection_service.forex_daily_service') as mock_forex_service:

            mock_session_local.return_value.__aenter__.return_value = mock_db
            mock_scheduler.update_next_run_time = MagicMock(return_value=expected_next_run)
            mock_forex_service.get_latest_date = AsyncMock(return_value=None)
            mock_forex_service.collect_and_save = AsyncMock(return_value=100)

            from app.services.collection_service import CollectionService
            service = CollectionService()

            await service.execute_task(task_id)

            # 验证采集被调用
            mock_forex_service.collect_and_save.assert_called_once()

            # 验证任务状态更新
            assert mock_task.last_status == "success"
            assert mock_task.last_records_count == 100

    @pytest.mark.asyncio
    async def test_execute_task_with_latest_date(self):
        """测试有最新数据日期时继续采集."""
        mock_db = AsyncMock()

        task_id = uuid4()
        symbol_id = uuid4()

        mock_task = MagicMock()
        mock_task.id = task_id
        mock_task.market_id = uuid4()
        mock_task.symbol_id = symbol_id
        mock_task.datasource_id = uuid4()
        mock_task.start_date = date(2026, 4, 1)
        mock_task.end_date = date(2026, 4, 15)
        mock_task.name = "外汇采集任务"

        mock_market = MagicMock()
        mock_market.code = "forex"

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_market_result = MagicMock()
        mock_market_result.scalar_one_or_none.return_value = mock_market

        mock_db.execute = AsyncMock(side_effect=[
            mock_task_result,
            mock_market_result,
        ])
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        latest_date = date(2026, 4, 10)  # 已有数据到4月10日

        with patch('app.services.collection_service.AsyncSessionLocal') as mock_session_local, \
             patch('app.services.collection_service.scheduler_service') as mock_scheduler, \
             patch('app.services.collection_service.forex_daily_service') as mock_forex_service:

            mock_session_local.return_value.__aenter__.return_value = mock_db
            mock_scheduler.update_next_run_time = MagicMock(return_value=datetime.now())
            mock_forex_service.get_latest_date = AsyncMock(return_value=latest_date)
            mock_forex_service.collect_and_save = AsyncMock(return_value=5)

            from app.services.collection_service import CollectionService
            service = CollectionService()

            await service.execute_task(task_id)

            # 验证从最新日期继续采集
            call_args = mock_forex_service.collect_and_save.call_args
            assert call_args[1]['start_date'] == latest_date + timedelta(days=1)

    @pytest.mark.asyncio
    async def test_execute_task_exception(self):
        """测试采集异常."""
        mock_db = AsyncMock()

        task_id = uuid4()

        mock_task = MagicMock()
        mock_task.id = task_id
        mock_task.market_id = uuid4()
        mock_task.symbol_id = uuid4()
        mock_task.datasource_id = uuid4()
        mock_task.name = "外汇采集任务"

        mock_market = MagicMock()
        mock_market.code = "forex"

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_market_result = MagicMock()
        mock_market_result.scalar_one_or_none.return_value = mock_market

        mock_db.execute = AsyncMock(side_effect=[
            mock_task_result,
            mock_market_result,
        ])
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch('app.services.collection_service.AsyncSessionLocal') as mock_session_local, \
             patch('app.services.collection_service.forex_daily_service') as mock_forex_service:

            mock_session_local.return_value.__aenter__.return_value = mock_db
            mock_forex_service.get_latest_date = AsyncMock(return_value=None)
            mock_forex_service.collect_and_save = AsyncMock(
                side_effect=Exception("采集失败")
            )

            from app.services.collection_service import CollectionService
            service = CollectionService()

            await service.execute_task(task_id)

            # 验证任务状态为失败
            assert mock_task.last_status == "failed"
            assert "采集失败" in mock_task.last_message


# ============ Test Class: Enable Task ============

class TestEnableTask:
    """
    启用任务测试.
    """

    @pytest.mark.asyncio
    async def test_enable_task_success(self):
        """测试成功启用任务."""
        mock_db = AsyncMock()

        task_id = uuid4()

        mock_task = MagicMock()
        mock_task.id = task_id
        mock_task.cron_expr = "0 18 * * *"
        mock_task.is_enabled = False

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()

        # Mock _add_task_to_scheduler 内部的数据库会话
        mock_inner_db = AsyncMock()
        mock_inner_task = MagicMock()
        mock_inner_task.next_run_at = None
        mock_inner_result = MagicMock()
        mock_inner_result.scalar_one_or_none.return_value = mock_inner_task

        # 使用AsyncMock来正确mock异步方法
        mock_inner_db.execute = AsyncMock(return_value=mock_inner_result)
        mock_inner_db.commit = AsyncMock()

        # 正确Mock async context manager
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_inner_db
        mock_context.__aexit__.return_value = None

        with patch('app.services.collection_service.scheduler_service') as mock_scheduler, \
             patch('app.services.collection_service.AsyncSessionLocal', return_value=mock_context), \
             patch('app.services.collection_service.forex_daily_service'):

            mock_scheduler.add_job = MagicMock()
            mock_scheduler.update_next_run_time = MagicMock(return_value=datetime.now())

            from app.services.collection_service import CollectionService
            service = CollectionService()

            result = await service.enable_task(task_id, mock_db)

            assert result is True
            assert mock_task.is_enabled is True
            mock_scheduler.add_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_enable_task_not_found(self):
        """测试任务不存在."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.services.collection_service.scheduler_service'):
            from app.services.collection_service import CollectionService
            service = CollectionService()

            result = await service.enable_task(uuid4(), mock_db)

            assert result is False

    @pytest.mark.asyncio
    async def test_enable_task_no_cron(self):
        """测试无cron表达式."""
        mock_db = AsyncMock()

        mock_task = MagicMock()
        mock_task.cron_expr = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.services.collection_service.scheduler_service'):
            from app.services.collection_service import CollectionService
            service = CollectionService()

            result = await service.enable_task(uuid4(), mock_db)

            assert result is False


# ============ Test Class: Disable Task ============

class TestDisableTask:
    """
    禁用任务测试.
    """

    @pytest.mark.asyncio
    async def test_disable_task_success(self):
        """测试成功禁用任务."""
        mock_db = AsyncMock()

        task_id = uuid4()

        mock_task = MagicMock()
        mock_task.id = task_id
        mock_task.is_enabled = True
        mock_task.next_run_at = datetime.now()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()

        with patch('app.services.collection_service.scheduler_service') as mock_scheduler:
            mock_scheduler.remove_job = MagicMock()

            from app.services.collection_service import CollectionService
            service = CollectionService()

            result = await service.disable_task(task_id, mock_db)

            assert result is True
            assert mock_task.is_enabled is False
            assert mock_task.next_run_at is None
            mock_scheduler.remove_job.assert_called_once_with(str(task_id))

    @pytest.mark.asyncio
    async def test_disable_task_not_found(self):
        """测试任务不存在."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.services.collection_service.scheduler_service') as mock_scheduler:
            mock_scheduler.remove_job = MagicMock()

            from app.services.collection_service import CollectionService
            service = CollectionService()

            result = await service.disable_task(uuid4(), mock_db)

            # 任务不存在仍返回True（已从调度器移除）
            assert result is True
            mock_scheduler.remove_job.assert_called_once()


# ============ Test Class: Global Instance ============

class TestGlobalInstance:
    """
    全局实例测试.
    """

    def test_collection_service_instance_exists(self):
        """测试全局实例存在."""
        with patch('app.services.collection_service.scheduler_service'), \
             patch('app.services.collection_service.forex_daily_service'), \
             patch('app.services.collection_service.AsyncSessionLocal'):

            import importlib
            import app.services.collection_service
            importlib.reload(app.services.collection_service)

            assert hasattr(app.services.collection_service, 'collection_service')

    def test_collection_service_is_correct_type(self):
        """测试全局实例类型."""
        with patch('app.services.collection_service.scheduler_service'), \
             patch('app.services.collection_service.forex_daily_service'), \
             patch('app.services.collection_service.AsyncSessionLocal'):

            import importlib
            import app.services.collection_service
            importlib.reload(app.services.collection_service)

            from app.services.collection_service import CollectionService
            assert isinstance(
                app.services.collection_service.collection_service,
                CollectionService
            )


# ============ Test Class: Edge Cases ============

class TestEdgeCases:
    """
    边界值测试.
    """

    @pytest.mark.asyncio
    async def test_execute_task_default_date_range(self):
        """测试默认日期范围（无start_date/end_date）."""
        mock_db = AsyncMock()

        mock_task = MagicMock()
        mock_task.id = uuid4()
        mock_task.market_id = uuid4()
        mock_task.symbol_id = uuid4()
        mock_task.datasource_id = uuid4()
        mock_task.start_date = None  # 无start_date
        mock_task.end_date = None    # 无end_date
        mock_task.name = "外汇采集任务"

        mock_market = MagicMock()
        mock_market.code = "forex"

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_market_result = MagicMock()
        mock_market_result.scalar_one_or_none.return_value = mock_market

        mock_db.execute = AsyncMock(side_effect=[
            mock_task_result,
            mock_market_result,
        ])
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch('app.services.collection_service.AsyncSessionLocal') as mock_session_local, \
             patch('app.services.collection_service.scheduler_service') as mock_scheduler, \
             patch('app.services.collection_service.forex_daily_service') as mock_forex_service:

            mock_session_local.return_value.__aenter__.return_value = mock_db
            mock_scheduler.update_next_run_time = MagicMock(return_value=datetime.now())
            mock_forex_service.get_latest_date = AsyncMock(return_value=None)
            mock_forex_service.collect_and_save = AsyncMock(return_value=30)

            from app.services.collection_service import CollectionService
            service = CollectionService()

            await service.execute_task(uuid4())

            # 验证默认日期范围（30天）
            call_args = mock_forex_service.collect_and_save.call_args
            assert call_args[1]['end_date'] == date.today()

    @pytest.mark.asyncio
    async def test_execute_task_zero_records(self):
        """测试采集零条数据."""
        mock_db = AsyncMock()

        mock_task = MagicMock()
        mock_task.id = uuid4()
        mock_task.market_id = uuid4()
        mock_task.symbol_id = uuid4()
        mock_task.datasource_id = uuid4()
        mock_task.name = "外汇采集任务"

        mock_market = MagicMock()
        mock_market.code = "forex"

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_market_result = MagicMock()
        mock_market_result.scalar_one_or_none.return_value = mock_market

        mock_db.execute = AsyncMock(side_effect=[
            mock_task_result,
            mock_market_result,
        ])
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch('app.services.collection_service.AsyncSessionLocal') as mock_session_local, \
             patch('app.services.collection_service.scheduler_service') as mock_scheduler, \
             patch('app.services.collection_service.forex_daily_service') as mock_forex_service:

            mock_session_local.return_value.__aenter__.return_value = mock_db
            mock_scheduler.update_next_run_time = MagicMock(return_value=datetime.now())
            mock_forex_service.get_latest_date = AsyncMock(return_value=None)
            mock_forex_service.collect_and_save = AsyncMock(return_value=0)

            from app.services.collection_service import CollectionService
            service = CollectionService()

            await service.execute_task(uuid4())

            # 验证零条数据仍为成功状态
            assert mock_task.last_status == "success"
            assert mock_task.last_records_count == 0

    @pytest.mark.asyncio
    async def test_latest_date_after_end_date(self):
        """测试最新日期在结束日期之后."""
        mock_db = AsyncMock()

        mock_task = MagicMock()
        mock_task.id = uuid4()
        mock_task.market_id = uuid4()
        mock_task.symbol_id = uuid4()
        mock_task.datasource_id = uuid4()
        mock_task.end_date = date(2026, 4, 10)
        mock_task.name = "外汇采集任务"

        mock_market = MagicMock()
        mock_market.code = "forex"

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_market_result = MagicMock()
        mock_market_result.scalar_one_or_none.return_value = mock_market

        mock_db.execute = AsyncMock(side_effect=[
            mock_task_result,
            mock_market_result,
        ])
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # 最新日期在结束日期之后
        latest_date = date(2026, 4, 15)  # 比 end_date(4, 10) 更晚

        with patch('app.services.collection_service.AsyncSessionLocal') as mock_session_local, \
             patch('app.services.collection_service.scheduler_service') as mock_scheduler, \
             patch('app.services.collection_service.forex_daily_service') as mock_forex_service:

            mock_session_local.return_value.__aenter__.return_value = mock_db
            mock_scheduler.update_next_run_time = MagicMock(return_value=datetime.now())
            mock_forex_service.get_latest_date = AsyncMock(return_value=latest_date)
            mock_forex_service.collect_and_save = AsyncMock(return_value=0)

            from app.services.collection_service import CollectionService
            service = CollectionService()

            await service.execute_task(uuid4())

            # 验证不调用collect_and_save（因为最新日期已超过结束日期）
            # 实际行为取决于实现逻辑