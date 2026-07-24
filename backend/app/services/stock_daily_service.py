"""
股票日线行情数据服务.

提供股票日线行情数据的采集、存储、查询功能.
支持A股/美股/港股通过market_id区分.

Author: FDAS Team
Created: 2026-04-23
"""

from typing import List, Optional, Dict, Any
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import insert
from uuid import UUID
import logging

from app.models.stock_daily import StockDaily
from app.models.stock_symbol import StockSymbol
from app.models.market import Market
from app.models.datasource import DataSource
from app.collectors.akshare_collector import AKShareCollector
from app.config.settings import settings

logger = logging.getLogger(__name__)


class StockDailyService:
    """
    股票日线行情数据服务.

    负责A股/美股/港股日线数据的采集、存储、查询等业务逻辑.
    """

    async def collect_and_save(
        self,
        db: AsyncSession,
        symbol_id: UUID,
        datasource_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        collector_config: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        采集并保存股票日线数据.

        Args:
            db: 数据库会话
            symbol_id: 标的ID
            datasource_id: 数据来源ID
            start_date: 开始日期（默认30天前）
            end_date: 结束日期（默认今天）
            collector_config: 采集器配置

        Returns:
            int: 保存的数据条数
        """
        # 获取标的信息
        result = await db.execute(
            select(StockSymbol).where(StockSymbol.id == symbol_id)
        )
        symbol = result.scalar_one_or_none()

        if not symbol:
            logger.error(f"股票标的不存在: {symbol_id}")
            return 0

        # 获取market_id
        market_id = symbol.market_id

        # 设置默认日期范围
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # 构建代码：仅A股需要 sh/sz/bj 前缀，港股/美股直接用原始代码
        code = symbol.code
        from app.models.market import Market as MarketModel
        market_result = await db.execute(select(MarketModel).where(MarketModel.id == market_id))
        market = market_result.scalar_one_or_none()
        is_cn = market and market.code == "stock_cn"

        if is_cn:
            if code.startswith("6"):
                full_code = f"sh{code}"
            elif code.startswith(("0", "3")):
                full_code = f"sz{code}"
            elif code.startswith(("4", "8", "9")):
                full_code = f"bj{code}"
            else:
                full_code = code
        else:
            full_code = code

        logger.info(f"开始采集股票数据: {symbol.name} ({code}), {start_date} ~ {end_date}")

        # 根据配置创建采集器
        if collector_config:
            collector = AKShareCollector(config=collector_config)
        else:
            collector = AKShareCollector()

        # 采集数据（使用新的统一入口）
        try:
            records = await collector.collect_daily(
                config=collector_config or {},
                symbol=full_code,
                start_date=start_date,
                end_date=end_date,
            )
        except NotImplementedError:
            logger.warning(f"股票采集接口尚未实现，跳过")
            return 0

        if not records:
            logger.warning(f"采集数据为空，跳过保存")
            return 0

        # 为每条记录添加symbol_id、market_id和datasource_id
        allowed_fields = {
            "date", "open", "high", "low", "close", "volume", "amount",
            "turnover", "change_pct", "change_amount", "amplitude",
            "is_suspended", "is_st", "updated_at"
        }
        cleaned_records = []
        for record in records:
            cleaned_record = {k: v for k, v in record.items() if k in allowed_fields}
            # Convert date string to date object for SQL
            date_val = cleaned_record.get("date")
            if isinstance(date_val, str):
                from datetime import date as date_cls
                cleaned_record["date"] = date_cls.fromisoformat(date_val)
            cleaned_record["symbol_id"] = symbol_id
            cleaned_record["market_id"] = market_id
            if datasource_id:
                cleaned_record["datasource_id"] = datasource_id
            cleaned_records.append(cleaned_record)

        # 批量保存
        saved_count = await self.save_stock_daily(db, cleaned_records)
        return saved_count

    async def get_stock_daily(
        self,
        db: AsyncSession,
        symbol_id: Optional[UUID] = None,
        market_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: Optional[int] = None,
    ) -> List[StockDaily]:
        """
        查询股票日线数据（按日期降序）.

        Args:
            db: 数据库会话
            symbol_id: 标的ID（可选）
            market_id: 市场ID（可选，用于区分A股/美股/港股）
            start_date: 开始日期
            end_date: 结束日期
            limit: 数据条数限制

        Returns:
            List[StockDaily]: 日线数据列表（按日期降序）
        """
        if limit is None:
            limit = settings.FX_DATA_LIMIT

        query = select(StockDaily)

        # 构建过滤条件
        conditions = []
        if symbol_id:
            conditions.append(StockDaily.symbol_id == symbol_id)
        if market_id:
            conditions.append(StockDaily.market_id == market_id)
        if start_date:
            conditions.append(StockDaily.date >= start_date)
        if end_date:
            conditions.append(StockDaily.date <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(StockDaily.date.desc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_stock_daily_asc(
        self,
        db: AsyncSession,
        symbol_id: Optional[UUID] = None,
        market_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: Optional[int] = None,
    ) -> List[StockDaily]:
        """
        查询股票日线数据（按日期升序，用于技术指标计算）.

        Args:
            db: 数据库会话
            symbol_id: 标的ID
            market_id: 市场ID
            start_date: 开始日期
            end_date: 结束日期
            limit: 数据条数限制

        Returns:
            List[StockDaily]: 日线数据列表（按日期升序）
        """
        if limit is None:
            limit = settings.FX_DATA_LIMIT

        query = select(StockDaily)

        conditions = []
        if symbol_id:
            conditions.append(StockDaily.symbol_id == symbol_id)
        if market_id:
            conditions.append(StockDaily.market_id == market_id)
        if start_date:
            conditions.append(StockDaily.date >= start_date)
        if end_date:
            conditions.append(StockDaily.date <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(StockDaily.date.asc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def save_stock_daily(
        self,
        db: AsyncSession,
        data: List[dict],
    ) -> int:
        """
        保存股票日线数据.

        使用ON CONFLICT处理重复数据（同一标的同一天同数据源）.
        注意：约束包含market_id以支持多市场共享表.

        Args:
            db: 数据库会话
            data: 日线数据列表

        Returns:
            int: 保存的数据条数
        """
        saved_count = 0

        for record in data:
            stmt = insert(StockDaily).values(**record)
            stmt = stmt.on_conflict_do_update(
                constraint="stock_daily_symbol_id_market_id_date_datasource_id_key",
                set_={
                    "open": stmt.excluded.open,
                    "high": stmt.excluded.high,
                    "low": stmt.excluded.low,
                    "close": stmt.excluded.close,
                    "volume": stmt.excluded.volume,
                    "amount": stmt.excluded.amount,
                    "turnover": stmt.excluded.turnover,
                    "change_pct": stmt.excluded.change_pct,
                    "change_amount": stmt.excluded.change_amount,
                    "amplitude": stmt.excluded.amplitude,
                    "is_suspended": stmt.excluded.is_suspended,
                    "is_st": stmt.excluded.is_st,
                    "updated_at": stmt.excluded.updated_at,
                }
            )
            await db.execute(stmt)
            saved_count += 1

        await db.commit()
        logger.info(f"成功保存 {saved_count} 条股票日线数据")
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
        query = select(StockDaily.date).where(StockDaily.symbol_id == symbol_id)
        query = query.order_by(StockDaily.date.desc()).limit(1)

        result = await db.execute(query)
        return result.scalar_one_or_none()


# 全局服务实例
stock_daily_service = StockDailyService()