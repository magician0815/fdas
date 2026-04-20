"""
采集任务协调服务.

负责协调采集任务的加载、执行和状态更新.

Author: FDAS Team
Created: 2026-04-10
Updated: 2026-04-10 - 适配ForexDailyService和symbol_id
"""

from typing import Optional
from uuid import UUID
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import json

from app.core.database import AsyncSessionLocal
from app.models.collection_task import CollectionTask
from app.models.collection_task_log import CollectionTaskLog
from app.models.datasource import DataSource
from app.models.market import Market
from app.models.forex_symbol import ForexSymbol
from app.services.scheduler_service import scheduler_service
from app.services.forex_daily_service import forex_daily_service
from app.config.logging import get_logger

logger = get_logger(__name__)


class CollectionService:
    """
    采集任务协调服务.

    负责：
    1. 加载已启用的任务到调度器
    2. 执行采集任务
    3. 更新任务状态和日志
    """

    async def load_enabled_tasks(self):
        """
        加载所有已启用的采集任务到调度器.

        应用启动时调用，从数据库读取is_enabled=True的任务并添加到调度器.
        """
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(CollectionTask).where(CollectionTask.is_enabled == True)
            )
            tasks = result.scalars().all()

            for task in tasks:
                if task.cron_expr:
                    await self._add_task_to_scheduler(task)
                    logger.info(f"加载任务到调度器: {task.name}")

            logger.info(f"已加载 {len(tasks)} 个采集任务到调度器")

    async def _add_task_to_scheduler(self, task: CollectionTask):
        """
        将任务添加到调度器.

        Args:
            task: 采集任务对象
        """
        scheduler_service.add_job(
            job_id=str(task.id),
            func=self.execute_task,
            cron_expr=task.cron_expr,
            task_id=task.id,
        )

        # 更新next_run_at
        async with AsyncSessionLocal() as db:
            next_run_time = scheduler_service.update_next_run_time(str(task.id))
            if next_run_time:
                result = await db.execute(
                    select(CollectionTask).where(CollectionTask.id == task.id)
                )
                db_task = result.scalar_one_or_none()
                if db_task:
                    db_task.next_run_at = next_run_time
                    await db.commit()

    async def execute_task(self, task_id: UUID):
        """
        执行采集任务（调度器回调函数）.

        Args:
            task_id: 任务ID
        """
        logger.info(f"开始执行采集任务: {task_id}")

        async with AsyncSessionLocal() as db:
            # 获取任务信息
            result = await db.execute(
                select(CollectionTask).where(CollectionTask.id == task_id)
            )
            task = result.scalar_one_or_none()

            if not task:
                logger.error(f"任务不存在: {task_id}")
                return

            # 获取市场信息
            result = await db.execute(
                select(Market).where(Market.id == task.market_id)
            )
            market = result.scalar_one_or_none()

            if not market:
                logger.error(f"市场不存在: {task.market_id}")
                return

            # 目前只支持外汇市场
            if market.code != "forex":
                logger.error(f"暂不支持市场类型: {market.name}")
                return

            # 创建执行日志
            log = CollectionTaskLog(
                task_id=task.id,
                run_at=datetime.now(timezone.utc),
                status="running",
            )
            db.add(log)
            await db.commit()
            await db.refresh(log)

            start_time = datetime.now(timezone.utc)

            try:
                # 确定采集日期范围
                start_date = task.start_date or (date.today() - timedelta(days=30))
                end_date = task.end_date or date.today()

                # 检查最新数据日期，从最新日期继续采集
                latest_date = await forex_daily_service.get_latest_date(db, task.symbol_id)
                if latest_date and latest_date < end_date:
                    start_date = latest_date + timedelta(days=1)

                # 获取数据源配置
                collector_config = None
                if task.datasource_id:
                    result = await db.execute(
                        select(DataSource).where(DataSource.id == task.datasource_id)
                    )
                    datasource = result.scalar_one_or_none()
                    if datasource and datasource.config_file:
                        try:
                            collector_config = json.loads(datasource.config_file)
                            logger.info(f"使用数据源配置: {datasource.name}")
                        except json.JSONDecodeError as e:
                            logger.warning(f"数据源配置JSON解析失败，使用默认: {e}")

                # 执行采集
                records_count = await forex_daily_service.collect_and_save(
                    db=db,
                    symbol_id=task.symbol_id,
                    datasource_id=task.datasource_id,
                    start_date=start_date,
                    end_date=end_date,
                    collector_config=collector_config,
                )

                # 更新日志
                duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                log.status = "success"
                log.records_count = records_count
                log.duration_ms = duration_ms
                log.message = f"成功采集 {records_count} 条数据"

                # 更新任务状态
                task.last_run_at = datetime.now(timezone.utc)
                task.last_status = "success"
                task.last_message = log.message
                task.last_records_count = records_count

                # 更新下次执行时间
                next_run_time = scheduler_service.update_next_run_time(str(task.id))
                if next_run_time:
                    task.next_run_at = next_run_time

                await db.commit()

                logger.info(f"任务执行成功: {task.name}, 采集 {records_count} 条数据")

            except Exception as e:
                # 更新日志为失败
                duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                log.status = "failed"
                log.message = str(e)
                log.duration_ms = duration_ms

                # 更新任务状态
                task.last_run_at = datetime.now(timezone.utc)
                task.last_status = "failed"
                task.last_message = str(e)

                await db.commit()

                logger.error(f"任务执行失败: {task.name}, 错误: {str(e)}")

    async def enable_task(self, task_id: UUID, db: AsyncSession) -> bool:
        """
        启用任务.

        Args:
            task_id: 任务ID
            db: 数据库会话

        Returns:
            bool: 是否成功
        """
        result = await db.execute(
            select(CollectionTask).where(CollectionTask.id == task_id)
        )
        task = result.scalar_one_or_none()

        if not task or not task.cron_expr:
            return False

        # 添加到调度器
        await self._add_task_to_scheduler(task)

        # 更新数据库状态
        task.is_enabled = True
        await db.commit()

        return True

    async def disable_task(self, task_id: UUID, db: AsyncSession) -> bool:
        """
        禁用任务.

        Args:
            task_id: 任务ID
            db: 数据库会话

        Returns:
            bool: 是否成功
        """
        # 从调度器移除
        scheduler_service.remove_job(str(task_id))

        # 更新数据库状态
        result = await db.execute(
            select(CollectionTask).where(CollectionTask.id == task_id)
        )
        task = result.scalar_one_or_none()

        if task:
            task.is_enabled = False
            task.next_run_at = None
            await db.commit()

        return True


# 全局服务实例
collection_service = CollectionService()