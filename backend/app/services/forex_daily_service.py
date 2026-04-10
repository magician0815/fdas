"""
外汇日线行情数据服务.

提供外汇日线行情数据的采集、存储、查询功能.

Author: FDAS Team
Created: 2026-04-10
"""

from typing import List, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from uuid import UUID
import logging

from app.models.forex_daily import ForexDaily
from app.models.forex_symbol import ForexSymbol
from app.models.datasource import DataSource
from app.collectors.akshare_collector import akshare_collector
from app.config.settings import settings

logger = logging.getLogger(__name__)


class ForexDailyService:
    """
    外汇日线行情数据服务.

    负责数据采集、存储、查询等业务逻辑.
    """

    async def collect_and_save(
        self,
        db: AsyncSession,
        symbol_id: UUID,
        datasource_id: Optional[UUID] = None,
        start_date: date = None,
        end_date: date = None,
    ) -> int:
        """
        采集并保存外汇日线数据.

        Args:
            db: 数据库会话
            symbol_id: 标的ID
            datasource_id: 数据来源ID
            start_date: 开始日期（默认30天前）
            end_date: 结束日期（默认今天）

        Returns:
            int: 保存的数据条数
        """
        # 获取标的信息
        result = await db.execute(
            select(ForexSymbol).where(ForexSymbol.id == symbol_id)
        )
        symbol = result.scalar_one_or_none()

        if not symbol:
            logger.error(f"标的不存在: {symbol_id}")
            return 0

        # 设置默认日期范围
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - __import__('datetime').timedelta(days=30)

        logger.info(f"开始采集并保存数据: {symbol.name} ({symbol.code}), {start_date} ~ {end_date}")

        # 采集数据
        records = await akshare_collector.collect_forex_hist(
            symbol_name=symbol.name,
            symbol_code=symbol.code,
            start_date=start_date,
            end_date=end_date,
        )

        if not records:
            logger.warning(f"采集数据为空，跳过保存")
            return 0

        # 为每条记录添加symbol_id和datasource_id
        for record in records:
            record["symbol_id"] = symbol_id
            if datasource_id:
                record["datasource_id"] = datasource_id

        # 批量保存
        saved_count = await self.save_forex_daily(db, records)
        return saved_count

    async def get_forex_daily(
        self,
        db: AsyncSession,
        symbol_id: Optional[UUID] = None,
        symbol_code: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: Optional[int] = None,
    ) -> List[ForexDaily]:
        """
        查询外汇日线数据（按日期降序）.

        Args:
            db: 数据库会话
            symbol_id: 标的ID
            symbol_code: 标的代码（需先查询symbols表获取ID）
            start_date: 开始日期
            end_date: 结束日期
            limit: 数据条数限制

        Returns:
            List[ForexDaily]: 日线数据列表（按日期降序）
        """
        if limit is None:
            limit = settings.FX_DATA_LIMIT

        # 如果提供symbol_code，先查询symbol_id
        if symbol_code and not symbol_id:
            result = await db.execute(
                select(ForexSymbol.id).where(ForexSymbol.code == symbol_code.upper())
            )
            symbol_id = result.scalar_one_or_none()
            if not symbol_id:
                return []

        query = select(ForexDaily)

        if symbol_id:
            query = query.where(ForexDaily.symbol_id == symbol_id)

        if start_date:
            query = query.where(ForexDaily.date >= start_date)
        if end_date:
            query = query.where(ForexDaily.date <= end_date)

        query = query.order_by(ForexDaily.date.desc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_forex_daily_asc(
        self,
        db: AsyncSession,
        symbol_id: Optional[UUID] = None,
        symbol_code: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: Optional[int] = None,
    ) -> List[ForexDaily]:
        """
        查询外汇日线数据（按日期升序，用于技术指标计算）.

        Args:
            db: 数据库会话
            symbol_id: 标的ID
            symbol_code: 标的代码
            start_date: 开始日期
            end_date: 结束日期
            limit: 数据条数限制

        Returns:
            List[ForexDaily]: 日线数据列表（按日期升序）
        """
        if limit is None:
            limit = settings.FX_DATA_LIMIT

        if symbol_code and not symbol_id:
            result = await db.execute(
                select(ForexSymbol.id).where(ForexSymbol.code == symbol_code.upper())
            )
            symbol_id = result.scalar_one_or_none()
            if not symbol_id:
                return []

        query = select(ForexDaily)

        if symbol_id:
            query = query.where(ForexDaily.symbol_id == symbol_id)

        if start_date:
            query = query.where(ForexDaily.date >= start_date)
        if end_date:
            query = query.where(ForexDaily.date <= end_date)

        query = query.order_by(ForexDaily.date.asc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def save_forex_daily(
        self,
        db: AsyncSession,
        data: List[dict],
    ) -> int:
        """
        保存外汇日线数据.

        使用ON CONFLICT处理重复数据（同一标的同一天同数据源）.

        Args:
            db: 数据库会话
            data: 日线数据列表（已转换格式）

        Returns:
            int: 保存的数据条数
        """
        saved_count = 0

        for record in data:
            stmt = insert(ForexDaily).values(**record)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_forex_daily_symbol_date_datasource",
                set_={
                    "open": stmt.excluded.open,
                    "high": stmt.excluded.high,
                    "low": stmt.excluded.low,
                    "close": stmt.excluded.close,
                    "change_pct": stmt.excluded.change_pct,
                    "change_amount": stmt.excluded.change_amount,
                    "amplitude": stmt.excluded.amplitude,
                    "updated_at": stmt.excluded.updated_at,
                }
            )
            await db.execute(stmt)
            saved_count += 1

        await db.commit()
        logger.info(f"成功保存 {saved_count} 条外汇日线数据")
        return saved_count

    async def get_latest_date(
        self,
        db: AsyncSession,
        symbol_id: UUID,
    ) -> Optional[date]:
        """
        获取指定标的的最新数据日期.

        Args:
            db: 数据库会话
            symbol_id: 标的ID

        Returns:
            Optional[date]: 最新日期，若无数据则返回None
        """
        query = select(ForexDaily.date).where(ForexDaily.symbol_id == symbol_id)
        query = query.order_by(ForexDaily.date.desc()).limit(1)

        result = await db.execute(query)
        return result.scalar_one_or_none()


# 全局服务实例
forex_daily_service = ForexDailyService()