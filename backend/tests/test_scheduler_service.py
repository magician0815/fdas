"""
任务调度服务测试.

为scheduler_service.py提供完整的单元测试覆盖，包含边界值测试。

测试目标:
- SchedulerService类初始化
- start: 启动调度器
- shutdown: 关闭调度器
- add_job: 添加定时任务
- remove_job: 移除定时任务
- pause_job: 暂停定时任务
- resume_job: 恢复定时任务
- get_job: 获取任务信息
- get_jobs: 获取所有任务信息
- update_next_run_time: 更新下次执行时间

覆盖率目标: 80%+

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime
from uuid import uuid4

# 注意：由于SchedulerService在模块加载时就初始化了全局实例
# 需要在导入前Mock相关依赖


# ============ Test Class: SchedulerService Init ============

class TestSchedulerServiceInit:
    """
    调度服务初始化测试.
    """

    def test_init_creates_scheduler_instance(self):
        """测试初始化创建调度器实例."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore') as mock_jobstore, \
             patch('app.services.scheduler_service.ThreadPoolExecutor') as mock_executor, \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            # 导入并创建实例
            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            assert service.scheduler is not None
            assert service._is_running is False
            mock_scheduler_class.assert_called_once()

    def test_init_uses_correct_timezone(self):
        """测试初始化使用正确的时区."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            # 验证时区参数
            call_kwargs = mock_scheduler_class.call_args[1]
            assert call_kwargs['timezone'] == 'Asia/Shanghai'

    def test_init_configures_jobstore(self):
        """测试初始化配置jobstore."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore') as mock_jobstore_class, \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler'):

            mock_jobstore = MagicMock()
            mock_jobstore_class.return_value = mock_jobstore

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            mock_jobstore_class.assert_called_once()

    def test_init_configures_executor(self):
        """测试初始化配置executor."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor') as mock_executor_class, \
             patch('app.services.scheduler_service.AsyncIOScheduler'):

            mock_executor = MagicMock()
            mock_executor_class.return_value = mock_executor

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            # 验证线程池大小
            mock_executor_class.assert_called_with(20)


# ============ Test Class: Start/Shutdown ============

class TestStartShutdown:
    """
    启动和关闭测试.
    """

    def test_start_calls_scheduler_start(self):
        """测试启动调用scheduler.start()."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            service.start()

            mock_scheduler.start.assert_called_once()
            assert service._is_running is True

    def test_start_skips_if_already_running(self):
        """测试已运行时跳过启动."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()
            service._is_running = True  # 设置为已运行

            service.start()

            mock_scheduler.start.assert_not_called()

    def test_shutdown_calls_scheduler_shutdown(self):
        """测试关闭调用scheduler.shutdown()."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()
            service._is_running = True

            service.shutdown()

            mock_scheduler.shutdown.assert_called_once_with(wait=True)
            assert service._is_running is False

    def test_shutdown_with_wait_false(self):
        """测试关闭不等待任务完成."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()
            service._is_running = True

            service.shutdown(wait=False)

            mock_scheduler.shutdown.assert_called_once_with(wait=False)

    def test_shutdown_skips_if_not_running(self):
        """测试未运行时跳过关闭."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()
            service._is_running = False

            service.shutdown()

            mock_scheduler.shutdown.assert_not_called()


# ============ Test Class: Add Job ============

class TestAddJob:
    """
    添加任务测试.
    """

    def test_add_job_success(self):
        """测试成功添加任务."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class, \
             patch('app.services.scheduler_service.CronTrigger') as mock_trigger_class:

            mock_scheduler = MagicMock()
            mock_job = MagicMock()
            mock_job.id = str(uuid4())
            mock_scheduler.add_job.return_value = mock_job
            mock_scheduler_class.return_value = mock_scheduler

            mock_trigger = MagicMock()
            mock_trigger_class.return_value = mock_trigger

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            job_id = service.add_job(
                job_id="test-job",
                func=lambda: None,
                cron_expr="0 18 * * *",
            )

            assert job_id == mock_job.id
            mock_scheduler.add_job.assert_called_once()
            mock_trigger_class.assert_called_once()

    def test_add_job_with_kwargs(self):
        """测试添加任务带参数."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class, \
             patch('app.services.scheduler_service.CronTrigger'):

            mock_scheduler = MagicMock()
            mock_job = MagicMock()
            mock_job.id = "test-job"
            mock_scheduler.add_job.return_value = mock_job
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            def dummy_func(x, y):
                return x + y

            job_id = service.add_job(
                job_id="test-job",
                func=dummy_func,
                cron_expr="30 9 * * 1",
                x=1,
                y=2,
            )

            # 验证kwargs被传递
            call_kwargs = mock_scheduler.add_job.call_args[1]
            assert call_kwargs['kwargs'] == {'x': 1, 'y': 2}

    def test_add_job_invalid_cron_format(self):
        """测试无效cron表达式."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            # 4字段而非5字段
            with pytest.raises(ValueError) as exc_info:
                service.add_job(
                    job_id="test-job",
                    func=lambda: None,
                    cron_expr="0 18 *",
                )

            assert "cron表达式格式错误" in str(exc_info.value)

    def test_add_job_6_field_cron(self):
        """测试6字段cron表达式（错误格式）."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            with pytest.raises(ValueError):
                service.add_job(
                    job_id="test-job",
                    func=lambda: None,
                    cron_expr="0 18 * * * *",  # 6字段
                )

    def test_add_job_replace_existing(self):
        """测试替换已存在的任务."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class, \
             patch('app.services.scheduler_service.CronTrigger'):

            mock_scheduler = MagicMock()
            mock_job = MagicMock()
            mock_job.id = "existing-job"
            mock_scheduler.add_job.return_value = mock_job
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            service.add_job(
                job_id="existing-job",
                func=lambda: None,
                cron_expr="0 18 * * *",
            )

            # 验证replace_existing参数
            call_kwargs = mock_scheduler.add_job.call_args[1]
            assert call_kwargs['replace_existing'] is True

    def test_add_job_cron_trigger_exception(self):
        """测试CronTrigger异常."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class, \
             patch('app.services.scheduler_service.CronTrigger') as mock_trigger_class:

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler
            mock_trigger_class.side_effect = Exception("Invalid trigger")

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            with pytest.raises(Exception) as exc_info:
                service.add_job(
                    job_id="test-job",
                    func=lambda: None,
                    cron_expr="0 18 * * *",
                )

            assert "Invalid trigger" in str(exc_info.value)


# ============ Test Class: Remove Job ============

class TestRemoveJob:
    """
    移除任务测试.
    """

    def test_remove_job_success(self):
        """测试成功移除任务."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            service.remove_job("test-job")

            mock_scheduler.remove_job.assert_called_once_with("test-job")

    def test_remove_job_nonexistent(self):
        """测试移除不存在任务（APScheduler会抛出异常）."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler.remove_job.side_effect = Exception("Job not found")
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            with pytest.raises(Exception):
                service.remove_job("nonexistent-job")


# ============ Test Class: Pause/Resume Job ============

class TestPauseResumeJob:
    """
    暂停和恢复任务测试.
    """

    def test_pause_job_success(self):
        """测试成功暂停任务."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            service.pause_job("test-job")

            mock_scheduler.pause_job.assert_called_once_with("test-job")

    def test_resume_job_success(self):
        """测试成功恢复任务."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            service.resume_job("test-job")

            mock_scheduler.resume_job.assert_called_once_with("test-job")


# ============ Test Class: Get Job ============

class TestGetJob:
    """
    获取任务信息测试.
    """

    def test_get_job_exists(self):
        """测试获取存在的任务."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_job = MagicMock()
            mock_job.id = "test-job"
            mock_job.next_run_time = datetime(2026, 4, 15, 18, 0)
            mock_job.trigger = MagicMock()
            str(mock_job.trigger)  # 确保可以转换为字符串
            mock_scheduler.get_job.return_value = mock_job
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            result = service.get_job("test-job")

            assert result is not None
            assert result['id'] == "test-job"
            assert result['next_run_time'] == datetime(2026, 4, 15, 18, 0)
            assert 'trigger' in result

    def test_get_job_not_exists(self):
        """测试获取不存在任务."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler.get_job.return_value = None
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            result = service.get_job("nonexistent-job")

            assert result is None

    def test_get_job_empty_id(self):
        """测试空任务ID."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler.get_job.return_value = None
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            result = service.get_job("")
            assert result is None


# ============ Test Class: Get Jobs ============

class TestGetJobs:
    """
    获取所有任务测试.
    """

    def test_get_jobs_multiple(self):
        """测试获取多个任务."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_jobs = []
            for i in range(3):
                job = MagicMock()
                job.id = f"job-{i}"
                job.next_run_time = datetime(2026, 4, 15, 9 + i, 0)
                job.trigger = MagicMock()
                mock_jobs.append(job)

            mock_scheduler.get_jobs.return_value = mock_jobs
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            result = service.get_jobs()

            assert len(result) == 3
            assert result[0]['id'] == "job-0"
            assert result[1]['id'] == "job-1"
            assert result[2]['id'] == "job-2"

    def test_get_jobs_empty(self):
        """测试无任务."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler.get_jobs.return_value = []
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            result = service.get_jobs()

            assert result == []
            assert len(result) == 0


# ============ Test Class: Update Next Run Time ============

class TestUpdateNextRunTime:
    """
    更新下次执行时间测试.
    """

    def test_update_next_run_time_success(self):
        """测试成功更新下次执行时间."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_job = MagicMock()
            expected_time = datetime(2026, 4, 15, 18, 0)
            mock_job.next_run_time = expected_time
            mock_scheduler.get_job.return_value = mock_job
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            result = service.update_next_run_time("test-job")

            assert result == expected_time

    def test_update_next_run_time_job_not_exists(self):
        """测试任务不存在."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler.get_job.return_value = None
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            result = service.update_next_run_time("nonexistent-job")

            assert result is None


# ============ Test Class: Global Instance ============

class TestGlobalInstance:
    """
    全局实例测试.
    """

    def test_scheduler_service_instance_exists(self):
        """测试全局实例存在."""
        # 注意：这个测试依赖真实导入，可能需要数据库连接
        # 为了避免导入错误，我们Mock整个导入过程
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler'):

            # 重新导入模块以获取Mock后的实例
            import importlib
            import app.services.scheduler_service
            importlib.reload(app.services.scheduler_service)

            # scheduler_service 应该存在
            assert hasattr(app.services.scheduler_service, 'scheduler_service')

    def test_scheduler_service_is_correct_type(self):
        """测试全局实例类型."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler'):

            import importlib
            import app.services.scheduler_service
            importlib.reload(app.services.scheduler_service)

            from app.services.scheduler_service import SchedulerService
            assert isinstance(
                app.services.scheduler_service.scheduler_service,
                SchedulerService
            )


# ============ Test Class: Edge Cases ============

class TestEdgeCases:
    """
    边界值测试.
    """

    def test_add_job_uuid_job_id(self):
        """测试UUID格式的任务ID."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class, \
             patch('app.services.scheduler_service.CronTrigger'):

            mock_scheduler = MagicMock()
            mock_job = MagicMock()
            uuid_str = str(uuid4())
            mock_job.id = uuid_str
            mock_scheduler.add_job.return_value = mock_job
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            result = service.add_job(
                job_id=uuid_str,
                func=lambda: None,
                cron_expr="0 18 * * *",
            )

            assert result == uuid_str

    def test_add_job_special_characters_in_id(self):
        """测试任务ID包含特殊字符."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class, \
             patch('app.services.scheduler_service.CronTrigger'):

            mock_scheduler = MagicMock()
            mock_job = MagicMock()
            mock_job.id = "job-with-dashes-and_underscores"
            mock_scheduler.add_job.return_value = mock_job
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            result = service.add_job(
                job_id="job-with-dashes-and_underscores",
                func=lambda: None,
                cron_expr="0 18 * * *",
            )

            assert "job-with-dashes-and_underscores" in result

    def test_cron_expression_wildcards(self):
        """测试通配符cron表达式."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class, \
             patch('app.services.scheduler_service.CronTrigger') as mock_trigger_class:

            mock_scheduler = MagicMock()
            mock_job = MagicMock()
            mock_job.id = "wildcard-job"
            mock_scheduler.add_job.return_value = mock_job
            mock_scheduler_class.return_value = mock_scheduler

            mock_trigger = MagicMock()
            mock_trigger_class.return_value = mock_trigger

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            # 每分钟执行
            service.add_job(
                job_id="wildcard-job",
                func=lambda: None,
                cron_expr="* * * * *",
            )

            # 验证CronTrigger使用通配符参数
            call_args = mock_trigger_class.call_args[1]
            assert call_args['minute'] == '*'
            assert call_args['hour'] == '*'

    def test_multiple_start_shutdown_cycles(self):
        """测试多次启动关闭循环."""
        with patch('app.services.scheduler_service.SQLAlchemyJobStore'), \
             patch('app.services.scheduler_service.ThreadPoolExecutor'), \
             patch('app.services.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            from app.services.scheduler_service import SchedulerService
            service = SchedulerService()

            # 第一次启动
            service.start()
            assert service._is_running is True
            assert mock_scheduler.start.call_count == 1

            # 第一次关闭
            service.shutdown()
            assert service._is_running is False
            assert mock_scheduler.shutdown.call_count == 1

            # 第二次启动
            service.start()
            assert service._is_running is True
            assert mock_scheduler.start.call_count == 2

            # 第二次关闭
            service.shutdown()
            assert service._is_running is False
            assert mock_scheduler.shutdown.call_count == 2