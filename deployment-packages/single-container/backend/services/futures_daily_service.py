"""
期货日线行情数据服务。

提供期货日线行情数据的采集、存储、查询功能。

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

from app.models.futures_daily import FuturesDaily
from app.models.futures_contract import FuturesContract
from app.models.futures_variety import FuturesVariety
from app.collectors.akshare_collector import AKShareCollector
from app.config.settings import settings

logger = logging.getLogger(__name__)


class FuturesDailyService:
    """
    期货日线行情数据服务。

    负责期货日线数据的采集、存储、查询等业务逻辑。
    """

    async def collect_and_save(
        self,
        db: AsyncSession,
        contract_id: UUID,
        datasource_id: Optional[UUID] = None,
        start_date: Optional[DateType] = None,
        end_date: Optional[DateType] = None,
        collector_config: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        采集并保存期货日线数据。

        Args:
            db: 数据库会话
            contract_id: 合约ID
            datasource_id: 数据来源ID
            start_date: 开始日期（默认30天前）
            end_date: 结束日期（默认今天）
            collector_config: 采集器配置

        Returns:
            int: 保存的数据条数
        """
        result = await db.execute(
            select(FuturesContract).where(FuturesContract.id == contract_id)
        )
        contract = result.scalar_one_or_none()

        if not contract:
            logger.error(f"期货合约不存在: {contract_id}")
            return 0

        if not end_date:
            end_date = DateType.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        logger.info(f"开始采集期货数据: {contract.contract_name} ({contract.contract_code}), {start_date} ~ {end_date}")

        collector = AKShareCollector(config=collector_config or {})

        try:
            records = await collector.collect_daily(
                config=collector_config or {},
                symbol=contract.contract_code,
                start_date=start_date,
                end_date=end_date,
            )
        except NotImplementedError:
            logger.warning(f"期货采集接口尚未实现跳过")
            return 0

        if not records:
            logger.warning(f"采集数据为空跳过保存")
            return 0

        allowed_fields = {
            "date", "open", "high", "low", "close", "settle_price",
            "volume", "open_interest", "turnover", "change_pct",
            "change_amount", "amplitude", "oi_change", "is_main_data",
            "adjusted_price", "updated_at"
        }
        cleaned_records = []
        for record in records:
            cleaned_record = {k: v for k, v in record.items() if k in allowed_fields}
            cleaned_record["contract_id"] = contract_id
            cleaned_record["variety_id"] = contract.variety_id
            if datasource_id:
                cleaned_record["datasource_id"] = datasource_id
            cleaned_records.append(cleaned_record)

        saved_count = await self.save_futures_daily(db, cleaned_records)
        return saved_count

    async def get_futures_daily(
        self,
        db: AsyncSession,
        contract_id: Optional[UUID] = None,
        variety_id: Optional[UUID] = None,
        start_date: Optional[DateType] = None,
        end_date: Optional[DateType] = None,
        is_main_data: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> List[FuturesDaily]:
        """
        查询期货日线数据（按日期降序）。

        Args:
            db: 数据库会话
            contract_id: 合约ID（可选）
            variety_id: 品种ID（可选）
            start_date: 开始日期
            end_date: 结束日期
            is_main_data: 是否仅查询主力合约数据
            limit: 数据条数限制

        Returns:
            List[FuturesDaily]: 日线数据列表（按日期降序）
        """
        if limit is None:
            limit = settings.FX_DATA_LIMIT

        query = select(FuturesDaily)

        conditions = []
        if contract_id:
            conditions.append(FuturesDaily.contract_id == contract_id)
        if variety_id:
            conditions.append(FuturesDaily.variety_id == variety_id)
        if start_date:
            conditions.append(FuturesDaily.date >= start_date)
        if end_date:
            conditions.append(FuturesDaily.date <= end_date)
        if is_main_data is not None:
            conditions.append(FuturesDaily.is_main_data == is_main_data)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(FuturesDaily.date.desc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_futures_daily_asc(
        self,
        db: AsyncSession,
        contract_id: Optional[UUID] = None,
        variety_id: Optional[UUID] = None,
        start_date: Optional[DateType] = None,
        end_date: Optional[DateType] = None,
        limit: Optional[int] = None,
    ) -> List[FuturesDaily]:
        """
        查询期货日线数据（按日期升序用于技术指标计算）。

        Args:
            db: 数据库会话
            contract_id: 合约ID
            variety_id: 品种ID
            start_date: 开始日期
            end_date: 结束日期
            limit: 数据条数限制

        Returns:
            List[FuturesDaily]: 日线数据列表（按日期升序）
        """
        if limit is None:
            limit = settings.FX_DATA_LIMIT

        query = select(FuturesDaily)

        conditions = []
        if contract_id:
            conditions.append(FuturesDaily.contract_id == contract_id)
        if variety_id:
            conditions.append(FuturesDaily.variety_id == variety_id)
        if start_date:
            conditions.append(FuturesDaily.date >= start_date)
        if end_date:
            conditions.append(FuturesDaily.date <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(FuturesDaily.date.asc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def save_futures_daily(
        self,
        db: AsyncSession,
        data: List[dict],
    ) -> int:
        """
        保存期货日线数据。

        使用ON CONFLICT处理重复数据。

        Args:
            db: 数据库会话
            data: 日线数据列表

        Returns:
            int: 保存的数据条数
        """
        saved_count = 0

        for record in data:
            stmt = insert(FuturesDaily).values(**record)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_futures_daily_contract_date_datasource",
                set_={
                    "open": stmt.excluded.open,
                    "high": stmt.excluded.high,
                    "low": stmt.excluded.low,
                    "close": stmt.excluded.close,
                    "settle_price": stmt.excluded.settle_price,
                    "volume": stmt.excluded.volume,
                    "open_interest": stmt.excluded.open_interest,
                    "turnover": stmt.excluded.turnover,
                    "change_pct": stmt.excluded.change_pct,
                    "change_amount": stmt.excluded.change_amount,
                    "amplitude": stmt.excluded.amplitude,
                    "oi_change": stmt.excluded.oi_change,
                    "is_main_data": stmt.excluded.is_main_data,
                    "adjusted_price": stmt.excluded.adjusted_price,
                    "updated_at": stmt.excluded.updated_at,
                }
            )
            await db.execute(stmt)
            saved_count += 1

        await db.commit()
        logger.info(f"成功保存 {saved_count} 条期货日线数据")
        return saved_count

    async def get_latest_date(
        self,
        db: AsyncSession,
        contract_id: UUID,
    ) -> Optional[DateType]:
        """
        获取指定合约的最新数据日期。

        Args:
            db: 数据库会话
            contract_id: 合约ID

        Returns:
            Optional[DateType]: 最新日期若无数据则返回None
        """
        query = select(FuturesDaily.date).where(FuturesDaily.contract_id == contract_id)
        query = query.order_by(FuturesDaily.date.desc()).limit(1)

        result = await db.execute(query)
        return result.scalar_one_or_none()


futures_daily_service = FuturesDailyService()