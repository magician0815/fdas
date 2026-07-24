"""
债券日线行情数据服务。

提供债券日线行情数据的采集、存储、查询功能。
支持国内/国际债券通过market_id区分.

Author: FDAS Team
Created: 2026-04-23
"""

from typing import List, Optional, Dict, Any
from datetime import date as DateType, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import insert
from uuid import UUID
import logging

from app.models.bond_daily import BondDaily
from app.models.bond_symbol import BondSymbol
from app.models.market import Market
from app.collectors.akshare_collector import AKShareCollector
from app.config.settings import settings

logger = logging.getLogger(__name__)


class BondDailyService:
    """
    债券日线行情数据服务。

    负责国内/国际债券日线数据的采集、存储、查询等业务逻辑.
    """

    async def collect_and_save(
        self,
        db: AsyncSession,
        symbol_id: UUID,
        datasource_id: Optional[UUID] = None,
        start_date: Optional[DateType] = None,
        end_date: Optional[DateType] = None,
        collector_config: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        采集并保存债券日线数据。

        Args:
            db: 数据库会话
            symbol_id: 债券ID
            datasource_id: 数据来源ID
            start_date: 开始日期（默认30天前）
            end_date: 结束日期（默认今天）
            collector_config: 采集器配置

        Returns:
            int: 保存的数据条数
        """
        result = await db.execute(
            select(BondSymbol).where(BondSymbol.id == symbol_id)
        )
        symbol = result.scalar_one_or_none()

        if not symbol:
            logger.error(f"债券标的不存在: {symbol_id}")
            return 0

        market_id = symbol.market_id

        if not end_date:
            end_date = DateType.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        logger.info(f"开始采集债券数据: {symbol.name} ({symbol.code}), {start_date} ~ {end_date}")

        collector = AKShareCollector(config=collector_config or {})

        try:
            records = await collector.collect_daily(
                config=collector_config or {},
                symbol=symbol.code,
                start_date=start_date,
                end_date=end_date,
            )
        except NotImplementedError:
            logger.warning(f"债券采集接口尚未实现跳过")
            return 0

        if not records:
            logger.warning(f"采集数据为空跳过保存")
            return 0

        allowed_fields = {
            "date", "open", "high", "low", "close", "yield_rate",
            "volume", "amount", "change_pct", "change_amount",
            "amplitude", "updated_at"
        }
        cleaned_records = []
        for record in records:
            cleaned_record = {k: v for k, v in record.items() if k in allowed_fields}
            cleaned_record["symbol_id"] = symbol_id
            cleaned_record["market_id"] = market_id
            if datasource_id:
                cleaned_record["datasource_id"] = datasource_id
            # 转换日期字符串为 date 对象
            date_val = cleaned_record.get("date")
            if isinstance(date_val, str):
                cleaned_record["date"] = DateType.fromisoformat(date_val[:10])
            cleaned_records.append(cleaned_record)

        saved_count = await self.save_bond_daily(db, cleaned_records)
        return saved_count

    async def get_bond_daily(
        self,
        db: AsyncSession,
        symbol_id: Optional[UUID] = None,
        market_id: Optional[UUID] = None,
        start_date: Optional[DateType] = None,
        end_date: Optional[DateType] = None,
        limit: Optional[int] = None,
    ) -> List[BondDaily]:
        """
        查询债券日线数据（按日期降序）。

        Args:
            db: 数据库会话
            symbol_id: 债券ID（可选）
            market_id: 市场ID（可选，用于区分国内/国际债券）
            start_date: 开始日期
            end_date: 结束日期
            limit: 数据条数限制

        Returns:
            List[BondDaily]: 日线数据列表（按日期降序）
        """
        if limit is None:
            limit = settings.FX_DATA_LIMIT

        query = select(BondDaily)

        conditions = []
        if symbol_id:
            conditions.append(BondDaily.symbol_id == symbol_id)
        if market_id:
            conditions.append(BondDaily.market_id == market_id)
        if start_date:
            conditions.append(BondDaily.date >= start_date)
        if end_date:
            conditions.append(BondDaily.date <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(BondDaily.date.desc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_bond_daily_asc(
        self,
        db: AsyncSession,
        symbol_id: Optional[UUID] = None,
        market_id: Optional[UUID] = None,
        start_date: Optional[DateType] = None,
        end_date: Optional[DateType] = None,
        limit: Optional[int] = None,
    ) -> List[BondDaily]:
        """
        查询债券日线数据（按日期升序用于技术指标计算）。

        Args:
            db: 数据库会话
            symbol_id: 债券ID
            market_id: 市场ID
            start_date: 开始日期
            end_date: 结束日期
            limit: 数据条数限制

        Returns:
            List[BondDaily]: 日线数据列表（按日期升序）
        """
        if limit is None:
            limit = settings.FX_DATA_LIMIT

        query = select(BondDaily)

        conditions = []
        if symbol_id:
            conditions.append(BondDaily.symbol_id == symbol_id)
        if market_id:
            conditions.append(BondDaily.market_id == market_id)
        if start_date:
            conditions.append(BondDaily.date >= start_date)
        if end_date:
            conditions.append(BondDaily.date <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(BondDaily.date.asc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def save_bond_daily(
        self,
        db: AsyncSession,
        data: List[dict],
    ) -> int:
        """
        保存债券日线数据。

        使用ON CONFLICT处理重复数据（同一债券同一天同数据源）。
        注意：约束包含market_id以支持多市场共享表。

        Args:
            db: 数据库会话
            data: 日线数据列表

        Returns:
            int: 保存的数据条数
        """
        saved_count = 0

        for record in data:
            stmt = insert(BondDaily).values(**record)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_bond_daily_symbol_market_date_ds",
                set_={
                    "open": stmt.excluded.open,
                    "high": stmt.excluded.high,
                    "low": stmt.excluded.low,
                    "close": stmt.excluded.close,
                    "yield_rate": stmt.excluded.yield_rate,
                    "volume": stmt.excluded.volume,
                    "amount": stmt.excluded.amount,
                    "change_pct": stmt.excluded.change_pct,
                    "change_amount": stmt.excluded.change_amount,
                    "amplitude": stmt.excluded.amplitude,
                    "updated_at": stmt.excluded.updated_at,
                }
            )
            await db.execute(stmt)
            saved_count += 1

        await db.commit()
        logger.info(f"成功保存 {saved_count} 条债券日线数据")
        return saved_count

    async def get_latest_date(
        self,
        db: AsyncSession,
        symbol_id: UUID,
    ) -> Optional[DateType]:
        """
        获取指定债券的最新数据日期。

        Args:
            db: 数据库会话
            symbol_id: 债券ID

        Returns:
            Optional[DateType]: 最新日期若无数据则返回None
        """
        query = select(BondDaily.date).where(BondDaily.symbol_id == symbol_id)
        query = query.order_by(BondDaily.date.desc()).limit(1)

        result = await db.execute(query)
        return result.scalar_one_or_none()


bond_daily_service = BondDailyService()