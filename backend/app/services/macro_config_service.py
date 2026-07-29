"""
宏观数据源配置管理服务.

提供配置的 CRUD 操作、验证和采集器工厂.

Author: FDAS Team
Created: 2026-07-29
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.macro_config import MacroDataSourceConfig
from app.models.macro_data import MacroDataPoint
from app.collectors.macro_base_collector import MacroBaseCollector
from app.collectors.macro_nyfed_excel import MacroNYFedExcelCollector
from app.collectors.macro_richmond_html import MacroRichmondHTMLCollector
from app.collectors.macro_fomc_sep import MacroFOMCSEPCollector
from app.collectors.macro_feds_notes import MacroFEDSNotesCollector
from app.collectors.macro_fred_csv import MacroFREDCSVCollector

logger = logging.getLogger(__name__)

# source_code -> 采集器类映射
COLLECTOR_CLASS_MAP = {
    "r-star-LW": MacroNYFedExcelCollector,
    "r-star-HLW": MacroNYFedExcelCollector,
    "r-star-LM": MacroRichmondHTMLCollector,
    "r-sep": MacroFOMCSEPCollector,
    "longer-run-neutral": MacroFEDSNotesCollector,
    "real_gdp": MacroFREDCSVCollector,
    "potential_gdp": MacroFREDCSVCollector,
    "core_pce": MacroFREDCSVCollector,
}


class MacroConfigService:
    """宏观数据源配置管理服务."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_configs(self) -> List[MacroDataSourceConfig]:
        """获取所有配置列表."""
        result = await self.db.execute(
            select(MacroDataSourceConfig).order_by(MacroDataSourceConfig.created_at)
        )
        return list(result.scalars().all())

    async def get_config(self, config_id: UUID) -> Optional[MacroDataSourceConfig]:
        """获取单个配置."""
        result = await self.db.execute(
            select(MacroDataSourceConfig).where(MacroDataSourceConfig.id == config_id)
        )
        return result.scalar_one_or_none()

    async def get_config_by_source_code(self, source_code: str) -> Optional[MacroDataSourceConfig]:
        """按 source_code 获取配置."""
        result = await self.db.execute(
            select(MacroDataSourceConfig).where(MacroDataSourceConfig.source_code == source_code)
        )
        return result.scalar_one_or_none()

    async def create_config(self, data: Dict[str, Any]) -> MacroDataSourceConfig:
        """创建新配置."""
        existing = await self.db.execute(
            select(MacroDataSourceConfig).where(MacroDataSourceConfig.source_code == data["source_code"])
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"数据源代码 '{data['source_code']}' 已存在")

        config = MacroDataSourceConfig(**data)
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        logger.info(f"创建宏观数据源配置: {config.name} ({config.source_code})")
        return config

    async def update_config(self, config_id: UUID, data: Dict[str, Any]) -> Optional[MacroDataSourceConfig]:
        """更新配置."""
        config = await self.get_config(config_id)
        if not config:
            return None

        for key, value in data.items():
            if value is not None and hasattr(config, key):
                setattr(config, key, value)

        await self.db.commit()
        await self.db.refresh(config)
        logger.info(f"更新宏观数据源配置: {config.name}")
        return config

    async def delete_config(self, config_id: UUID) -> bool:
        """删除配置(级联删除关联数据)."""
        config = await self.get_config(config_id)
        if not config:
            return False

        await self.db.delete(config)
        await self.db.commit()
        logger.info(f"删除宏观数据源配置: {config.name}")
        return True

    async def get_last_publish_date(self, config_id: UUID) -> Optional[Any]:
        """获取某配置下数据的最大 publish_date，用于增量采集."""
        result = await self.db.execute(
            select(func.max(MacroDataPoint.publish_date)).where(
                MacroDataPoint.config_id == config_id
            )
        )
        return result.scalar()

    def config_to_dict(self, config: MacroDataSourceConfig) -> Dict[str, Any]:
        """将 ORM 对象转换为采集器所需的字典格式."""
        return {
            "id": config.id,
            "name": config.name,
            "source_code": config.source_code,
            "source_type": config.source_type,
            "description": config.description,
            "url": config.url,
            "parse_engine": config.parse_engine,
            "parse_config": config.parse_config or {},
            "headers": config.headers or {},
            "request_method": config.request_method,
            "timeout_seconds": config.timeout_seconds,
            "retry_max_attempts": config.retry_max_attempts,
            "retry_backoff_factor": config.retry_backoff_factor,
        }

    def create_collector(self, config: MacroDataSourceConfig) -> Optional[MacroBaseCollector]:
        """根据配置创建对应的采集器实例."""
        collector_class = COLLECTOR_CLASS_MAP.get(config.source_code)
        if not collector_class:
            logger.warning(f"未知的数据源代码: {config.source_code}，无对应采集器")
            return None

        config_dict = self.config_to_dict(config)
        return collector_class(config_dict)
