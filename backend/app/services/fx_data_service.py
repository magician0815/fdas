"""
汇率数据服务.

提供汇率数据的采集、存储、查询功能.

Author: FDAS Team
Created: 2026-04-03
"""

from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.models.fx_data import FXData
from app.collectors.akshare_collector import AKShareCollector
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class FXDataService:
    """
    汇率数据服务.

    负责数据采集、存储、查询等业务逻辑.
    """

    def __init__(self):
        self.collector = AKShareCollector()

    async def get_fx_data(
        self,
        db: AsyncSession,
        symbol: str = "USDCNH",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = None,
    ) -> List[FXData]:
        """
        查询汇率数据.

        Args:
            db: 数据库会话
            symbol: 汇率符号
            start_date: 开始日期
            end_date: 结束日期
            limit: 数据条数限制

        Returns:
            List[FXData]: 汇率数据列表
        """
        if limit is None:
            limit = settings.FX_DATA_LIMIT

        query = select(FXData).where(FXData.symbol == symbol)

        if start_date:
            query = query.where(FXData.date >= start_date)
        if end_date:
            query = query.where(FXData.date <= end_date)

        query = query.order_by(FXData.date.desc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def save_fx_data(
        self,
        db: AsyncSession,
        data: List[dict],
    ) -> int:
        """
        保存汇率数据.

        使用ON CONFLICT处理重复数据.

        Args:
            db: 数据库会话
            data: 汇率数据列表

        Returns:
            int: 保存的数据条数
        """
        for record in data:
            stmt = insert(FXData).values(**record)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_fx_data_symbol_date",
                set_=dict(
                    open=stmt.excluded.open,
                    high=stmt.excluded.high,
                    low=stmt.excluded.low,
                    close=stmt.excluded.close,
                    volume=stmt.excluded.volume,
                )
            )
            await db.execute(stmt)

        await db.commit()
        logger.info(f"保存{len(data)}条汇率数据")
        return len(data)


# 全局服务实例
fx_data_service = FXDataService()