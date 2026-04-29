"""
任务调度服务.

使用APScheduler实现定时任务调度.

Author: FDAS Team
Created: 2026-04-10
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from typing import Callable, List, Optional
from uuid import UUID
from datetime import datetime
import logging

from app.config.settings import settings
from app.config.logging import get_logger

logger = get_logger(__name__)


class SchedulerService:
    """
    任务调度服务.

    管理APScheduler任务配置和执行.
    """

    def __init__(self):
        """初始化调度器."""
        # 配置jobstore（使用PostgreSQL）
        jobstores = {
            'default': SQLAlchemyJobStore(
                url=settings.DATABASE_URL.replace('+asyncpg', ''),
                tablename='apscheduler_jobs',
            )
        }

        # 配置executor
        executors = {
            'default': ThreadPoolExecutor(20),
        }

        # 创建调度器
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            timezone='Asia/Shanghai',
        )

        self._is_running = False

    def start(self):
        """
        启动调度器.

        启动后会自动加载apscheduler_jobs表中保存的任务.
        """
        if self._is_running:
            logger.warning("调度器已运行，跳过启动")
            return

        self.scheduler.start()
        self._is_running = True
        logger.info("APScheduler调度器已启动")

    def shutdown(self, wait: bool = True):
        """
        关闭调度器.

        Args:
            wait: 是否等待正在执行的任务完成
        """
        if not self._is_running:
            return

        self.scheduler.shutdown(wait=wait)
        self._is_running = False
        logger.info("APScheduler调度器已关闭")

    def add_job(
        self,
        job_id: str,
        func: Callable,
        cron_expr: str,
        **kwargs,
    ) -> str:
        """
        添加定时任务.

        Args:
            job_id: 任务ID（通常使用UUID字符串）
            func: 执行函数
            cron_expr: cron表达式（如 "0 18 * * *"）
            **kwargs: 传递给func的参数

        Returns:
            str: 任务ID

        Raises:
            ValueError: cron表达式格式错误
        """
        try:
            # 解析cron表达式（5字段格式）
            parts = cron_expr.split()
            if len(parts) != 5:
                raise ValueError(f"cron表达式格式错误，应为5字段: {cron_expr}")

            trigger = CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4],
                timezone='Asia/Shanghai',
            )

            job = self.scheduler.add_job(
                id=job_id,
                func=func,
                trigger=trigger,
                kwargs=kwargs,
                replace_existing=True,  # 替换已存在的同名任务
            )

            logger.info(f"添加定时任务: {job_id}, cron: {cron_expr}")
            return job.id

        except Exception as e:
            logger.error(f"添加任务失败: {str(e)}")
            raise

    def remove_job(self, job_id: str):
        """
        移除定时任务.

        Args:
            job_id: 任务ID
        """
        self.scheduler.remove_job(job_id)
        logger.info(f"移除定时任务: {job_id}")

    def pause_job(self, job_id: str):
        """
        暂停定时任务.

        Args:
            job_id: 任务ID
        """
        self.scheduler.pause_job(job_id)
        logger.info(f"暂停定时任务: {job_id}")

    def resume_job(self, job_id: str):
        """
        恢复定时任务.

        Args:
            job_id: 任务ID
        """
        self.scheduler.resume_job(job_id)
        logger.info(f"恢复定时任务: {job_id}")

    def get_job(self, job_id: str) -> Optional[dict]:
        """
        获取任务信息.

        Args:
            job_id: 任务ID

        Returns:
            Optional[dict]: 任务信息，若不存在则返回None
        """
        job = self.scheduler.get_job(job_id)
        if not job:
            return None

        return {
            "id": job.id,
            "next_run_time": job.next_run_time,
            "trigger": str(job.trigger),
        }

    def get_jobs(self) -> List[dict]:
        """
        获取所有任务信息.

        Returns:
            List[dict]: 任务列表
        """
        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "next_run_time": job.next_run_time,
                "trigger": str(job.trigger),
            }
            for job in jobs
        ]

    def update_next_run_time(self, job_id: str) -> Optional[datetime]:
        """
        更新并返回任务的下次执行时间.

        Args:
            job_id: 任务ID

        Returns:
            Optional[datetime]: 下次执行时间
        """
        job = self.scheduler.get_job(job_id)
        if job:
            return job.next_run_time
        return None


# 全局调度器实例
scheduler_service = SchedulerService()