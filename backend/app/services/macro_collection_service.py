"""
宏观数据采集编排服务.

负责:
- 全量/增量采集调度
- 调度器注册/注销
- 采集日志记录
- 状态更新

Author: FDAS Team
Created: 2026-07-29
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.macro_config import MacroDataSourceConfig
from app.models.macro_data import MacroDataPoint
from app.models.macro_log import MacroCollectionLog
from app.services.macro_config_service import MacroConfigService
from app.services.scheduler_service import scheduler_service

logger = logging.getLogger(__name__)


class MacroCollectionService:
    """宏观数据采集编排服务."""

    async def load_enabled_configs(self):
        """应用启动时加载所有已启用的配置到调度器."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MacroDataSourceConfig).where(MacroDataSourceConfig.is_enabled == True)
            )
            configs = result.scalars().all()

            for config in configs:
                if config.cron_expr:
                    await self._add_to_scheduler(db, config)

            logger.info(f"已加载 {len(configs)} 个宏观数据源到调度器")

    async def _add_to_scheduler(self, db: AsyncSession, config: MacroDataSourceConfig):
        """将配置添加到调度器."""
        try:
            scheduler_service.add_job(
                job_id=f"macro-{config.id}",
                func=self.collect,
                cron_expr=config.cron_expr,
                config_id=config.id,
                full=False,
            )
            next_run = scheduler_service.update_next_run_time(f"macro-{config.id}")
            logger.info(f"宏观数据源调度注册: {config.source_code}, cron={config.cron_expr}, next={next_run}")
        except Exception as e:
            logger.error(f"调度注册失败: {config.source_code}: {e}")

    async def _remove_from_scheduler(self, config_id: UUID):
        """从调度器移除."""
        try:
            scheduler_service.remove_job(f"macro-{config_id}")
        except Exception:
            pass

    async def collect(self, config_id: UUID, full: bool = False):
        """
        执行采集任务(调度器回调).

        Args:
            config_id: 配置ID
            full: True=全量采集, False=增量采集
        """
        config_id_str = str(config_id)
        logger.info(f"开始宏观数据采集: config={config_id_str}, full={full}")

        async with AsyncSessionLocal() as db:
            config_service = MacroConfigService(db)
            config = await config_service.get_config(config_id)
            if not config:
                logger.error(f"配置不存在: {config_id_str}")
                return

            collector = config_service.create_collector(config)
            if not collector:
                logger.error(f"无法创建采集器: {config.source_code}")
                return

            # 创建日志
            log = MacroCollectionLog(
                config_id=config.id,
                run_at=datetime.now(timezone.utc),
                status="running",
                is_full=full,
            )
            db.add(log)
            await db.commit()
            await db.refresh(log)

            start_time = datetime.now(timezone.utc)

            try:
                # 确定增量起点
                last_date = None
                if not full:
                    last_date = await config_service.get_last_publish_date(config.id)

                # 执行采集
                records = await collector.collect(last_publish_date=last_date)

                # 入库(使用 INSERT ... ON CONFLICT DO NOTHING 跳过重复)
                from sqlalchemy.dialects.postgresql import insert as pg_insert
                saved_count = 0
                for record in records:
                    stmt = pg_insert(MacroDataPoint).values(**record)
                    stmt = stmt.on_conflict_do_nothing(
                        constraint="uq_macro_data_point"
                    )
                    result = await db.execute(stmt)
                    saved_count += result.rowcount
                await db.commit()

                # 更新日志
                duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                log.status = "success" if saved_count > 0 else "partial"
                log.records_count = saved_count
                log.duration_ms = duration_ms
                log.message = f"{'全量' if full else '增量'}采集完成: {saved_count} 条记录"

                # 更新配置状态
                config.last_collected_at = datetime.now(timezone.utc)
                config.last_status = log.status
                config.last_message = log.message
                config.last_records_count = saved_count

                await db.commit()
                logger.info(f"采集完成: {config.source_code}, 入库 {saved_count} 条, 耗时 {duration_ms}ms")

            except Exception as e:
                duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                log.status = "failed"
                log.records_count = 0
                log.duration_ms = duration_ms
                log.message = str(e)[:500]
                log.error_detail = str(e)[:2000]

                config.last_collected_at = datetime.now(timezone.utc)
                config.last_status = "failed"
                config.last_message = str(e)[:200]

                await db.commit()
                logger.error(f"采集失败: {config.source_code}: {e}")

    async def trigger_collect(self, config_id: UUID, full: bool = False) -> str:
        """
        手动触发一次采集.

        Returns:
            描述信息
        """
        await self.collect(config_id, full=full)
        return "采集任务已执行"

    async def enable_schedule(self, config_id: UUID, db: AsyncSession) -> bool:
        """启用定时调度."""
        config_service = MacroConfigService(db)
        config = await config_service.get_config(config_id)
        if not config or not config.cron_expr:
            return False

        await self._add_to_scheduler(db, config)
        config.is_enabled = True
        await db.commit()
        return True

    async def disable_schedule(self, config_id: UUID, db: AsyncSession) -> bool:
        """禁用定时调度."""
        await self._remove_from_scheduler(config_id)

        config_service = MacroConfigService(db)
        config = await config_service.get_config(config_id)
        if config:
            config.is_enabled = False
            await db.commit()

        return True


# 全局实例
macro_collection_service = MacroCollectionService()
