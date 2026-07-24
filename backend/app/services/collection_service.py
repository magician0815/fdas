"""
采集任务协调服务.

负责协调采集任务的加载、执行和状态更新.
支持全部7个市场: forex, stock_cn, stock_us, stock_hk, futures_cn, bond_cn, bond_us.

Author: FDAS Team
Created: 2026-04-10
Updated: 2026-04-29 - 多市场采集支持
"""

from typing import Optional, List, Dict
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
from app.services.scheduler_service import scheduler_service
from app.services.forex_daily_service import forex_daily_service
from app.services.stock_daily_service import stock_daily_service
from app.services.futures_daily_service import futures_daily_service
from app.services.bond_daily_service import bond_daily_service
from app.config.logging import get_logger

logger = get_logger(__name__)


# 市场代码 → 服务映射
MARKET_SERVICE_MAP = {
    "forex": forex_daily_service,
    "crypto": forex_daily_service,
    "stock_cn": stock_daily_service,
    "stock_us": stock_daily_service,
    "stock_hk": stock_daily_service,
    "futures_cn": futures_daily_service,
    "futures_intl": futures_daily_service,
    "bond_cn": bond_daily_service,
    "bond_us": bond_daily_service,
}

# 支持的市场代码
SUPPORTED_MARKETS = frozenset(MARKET_SERVICE_MAP.keys())


class CollectionService:
    """
    采集任务协调服务.

    负责：
    1. 加载已启用的任务到调度器
    2. 执行采集任务（多市场路由）
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

    async def _resolve_futures_symbols(
        self, db: AsyncSession, symbol_id_list: List[UUID]
    ) -> List[UUID]:
        """期货品种ID → 合约ID 解析，非期货市场直接返回原列表."""
        from app.models.futures_contract import FuturesContract as FC
        from app.models.futures_variety import FuturesVariety as FV

        resolved_ids = []
        for sid in symbol_id_list:
            ck = await db.execute(select(FC).where(FC.id == sid))
            if ck.scalar_one_or_none():
                resolved_ids.append(sid)
                continue
            # 非合约ID，尝试作为品种解析
            vr = await db.execute(select(FV).where(FV.id == sid))
            variety = vr.scalar_one_or_none()
            if variety:
                mc = await db.execute(
                    select(FC).where(FC.variety_id == sid, FC.is_main_contract == True)
                )
                contract = mc.scalar_one_or_none()
                if not contract:
                    contract = FC(
                        variety_id=sid,
                        contract_code=f"{variety.code}9999",
                        contract_name=f"{variety.name}连续",
                        contract_month="202609",
                        year="2026", month="09",
                        last_trade_date=date.today().replace(year=date.today().year + 1),
                        is_main_contract=True, is_active=True,
                    )
                    db.add(contract)
                    await db.flush()
                resolved_ids.append(contract.id)
            else:
                resolved_ids.append(sid)
        return resolved_ids

    async def _collect_all_symbols(
        self,
        db: AsyncSession,
        task: CollectionTask,
        market,
        service,
        symbol_id_list: List[UUID],
        collector_config: Optional[Dict],
        log: CollectionTaskLog,
        start_time: datetime,
    ) -> Dict:
        """遍历每个标的采集数据，带指数退避重试机制.

        Returns:
            {"total_records": int, "symbol_results": list, "failed_ids": list}
        """
        import asyncio as _asyncio
        import random as _random

        MAX_RETRIES = 5
        RETRY_BACKOFF = 3
        JITTER = 0.5

        total_records = 0
        symbol_results = []
        failed_ids = []

        for sid_idx, sid in enumerate(symbol_id_list):
            sid_str = str(sid)
            sid_success = False
            sid_records = 0
            sid_error = None
            attempt = 0

            log.message = f"正在采集标的 {sid_idx + 1}/{len(symbol_id_list)} (第1次尝试)..."
            log.records_count = total_records
            log.duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            await db.commit()

            for attempt in range(MAX_RETRIES):
                try:
                    if attempt > 0:
                        log.message = f"标的 {sid_idx + 1}/{len(symbol_id_list)} 第{attempt + 1}次重试..."
                        await db.commit()

                    start_date = task.start_date or (date.today() - timedelta(days=30))
                    end_date = task.end_date or date.today()

                    collect_kwargs = {
                        "db": db,
                        "datasource_id": task.datasource_id,
                        "start_date": start_date,
                        "end_date": end_date,
                        "collector_config": collector_config,
                    }
                    if market.code.startswith("futures"):
                        collect_kwargs["contract_id"] = sid
                    else:
                        collect_kwargs["symbol_id"] = sid

                    n = await service.collect_and_save(**collect_kwargs)
                    sid_records = n
                    sid_success = True
                    sid_error = None
                    break
                except Exception as e:
                    sid_error = str(e)
                    if attempt < MAX_RETRIES - 1:
                        wait = max(0.5, RETRY_BACKOFF ** attempt * (1 + _random.uniform(-JITTER, JITTER)))
                        safe_err = sid_error.replace('\n', ' ').replace('\r', '')[:100] if sid_error else ''
                        log.message = f"标的 {sid_idx + 1} 第{attempt + 1}次失败, {wait:.0f}s后重试: {safe_err}"
                        await db.commit()
                        logger.warning(f"标的 {sid_str} 第{attempt + 1}/{MAX_RETRIES}次失败，{wait:.1f}s后重试: {sid_error[:80]}")
                        await _asyncio.sleep(wait)
                    else:
                        logger.error(f"标的 {sid_str} 重试{MAX_RETRIES}次均失败: {sid_error[:200]}")

            total_records += sid_records
            symbol_results.append({
                "symbol_id": sid_str,
                "success": sid_success,
                "records": sid_records,
                "error": sid_error[:200] if sid_error else None,
                "retries": min(attempt + 1, MAX_RETRIES) if not sid_success else attempt + 1,
            })
            if not sid_success:
                failed_ids.append(sid_str)

            interim_duration = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            log.records_count = total_records
            log.duration_ms = interim_duration
            log.symbol_results = list(symbol_results)
            log.failed_symbols = list(failed_ids) if failed_ids else None
            log.message = f"已完成 {sid_idx + 1}/{len(symbol_id_list)} 标的, 累计 {total_records} 条数据"
            await db.commit()
            await db.refresh(log)

        return {
            "total_records": total_records,
            "symbol_results": symbol_results,
            "failed_ids": failed_ids,
        }

    async def execute_task(self, task_id: UUID):
        """
        执行采集任务（调度器回调函数，支持多市场路由）.

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

            if market.code not in SUPPORTED_MARKETS:
                logger.error(f"不支持的市场类型: {market.name} ({market.code})")
                return

            service = MARKET_SERVICE_MAP[market.code]

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
                # 获取标的列表
                symbol_id_list = task.symbol_ids or []
                if not symbol_id_list and task.symbol_id:
                    symbol_id_list = [task.symbol_id]
                if not symbol_id_list:
                    log.status = "failed"
                    log.message = "任务未配置标的"
                    await db.commit()
                    return

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

                # 期货：品种ID → 合约ID 解析
                if market.code.startswith("futures"):
                    symbol_id_list = await self._resolve_futures_symbols(db, symbol_id_list)

                # 遍历每个标的采集数据
                collect_result = await self._collect_all_symbols(
                    db, task, market, service, symbol_id_list, collector_config, log, start_time
                )

                records_count = collect_result["total_records"]
                symbol_results = collect_result["symbol_results"]
                failed_ids = collect_result["failed_ids"]

                # 更新日志最终状态
                duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                log.records_count = records_count
                log.duration_ms = duration_ms
                log.symbol_results = symbol_results
                log.failed_symbols = failed_ids if failed_ids else None

                success_count = sum(1 for r in symbol_results if r["success"])
                fail_count = len(failed_ids)
                if fail_count == 0:
                    log.status = "success"
                    log.message = f"全部完成: {success_count}个标的, {records_count}条数据"
                elif fail_count == len(symbol_id_list):
                    log.status = "failed"
                    log.message = f"全部失败: {fail_count}个标的均采集失败"
                else:
                    log.status = "partial"
                    log.message = f"部分完成: {success_count}/{len(symbol_id_list)}个标的成功, {records_count}条数据, {fail_count}个失败"

                # 更新任务状态
                task.last_run_at = datetime.now(timezone.utc)
                task.last_status = log.status
                task.last_message = log.message
                task.last_records_count = records_count

                next_run_time = scheduler_service.update_next_run_time(str(task.id))
                if next_run_time:
                    task.next_run_at = next_run_time

                await db.commit()
                logger.info(f"任务执行成功: {task.name} ({market.name}), 采集 {records_count} 条数据")

            except Exception as e:
                duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                log.status = "failed"
                log.message = str(e)
                log.duration_ms = duration_ms

                task.last_run_at = datetime.now(timezone.utc)
                task.last_status = "failed"
                task.last_message = str(e)

                await db.commit()
                logger.error(f"任务执行失败: {task.name} ({market.name}), 错误: {str(e)}")

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

        await self._add_task_to_scheduler(task)
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
        scheduler_service.remove_job(str(task_id))

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
