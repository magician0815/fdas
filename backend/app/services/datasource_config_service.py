"""
数据源配置管理服务.

提供数据源配置验证、存取、导入导出功能。

Author: FDAS Team
Created: 2026-04-21
"""

import json
import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.datasource import DataSource
from app.schemas.datasource_config_schema import (
    validate_config_json,
    get_default_forex_config,
    DatasourceConfigSchema,
)

logger = logging.getLogger(__name__)


class DatasourceConfigService:
    """数据源配置管理服务。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_config(self, datasource_id: UUID) -> Optional[dict]:
        """
        获取数据源配置。

        Args:
            datasource_id: 数据源ID

        Returns:
            配置字典或None
        """
        result = await self.db.execute(
            select(DataSource).where(DataSource.id == datasource_id)
        )
        datasource = result.scalar_one_or_none()

        if not datasource:
            return None

        if datasource.config_file:
            try:
                return json.loads(datasource.config_file)
            except json.JSONDecodeError:
                logger.error(f"数据源配置JSON解析失败: {datasource_id}")
                return None
        return None

    async def save_config(self, datasource_id: UUID, config_json: str) -> tuple[bool, str]:
        """
        保存数据源配置。

        Args:
            datasource_id: 数据源ID
            config_json: 配置JSON字符串

        Returns:
            (是否成功, 错误消息)
        """
        # 验证配置
        is_valid, error_msg, config_dict = validate_config_json(config_json)
        if not is_valid:
            return False, error_msg

        # 查询数据源
        result = await self.db.execute(
            select(DataSource).where(DataSource.id == datasource_id)
        )
        datasource = result.scalar_one_or_none()

        if not datasource:
            return False, "数据源不存在"

        # 保存配置
        datasource.config_file = config_json
        datasource.config_version = config_dict.get("version", "1.0")
        datasource.config_updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(datasource)

        return True, ""

    async def export_config(self, datasource_id: UUID) -> Optional[str]:
        """
        导出数据源配置。

        Args:
            datasource_id: 数据源ID

        Returns:
            配置JSON字符串或None
        """
        result = await self.db.execute(
            select(DataSource).where(DataSource.id == datasource_id)
        )
        datasource = result.scalar_one_or_none()

        if not datasource:
            return None

        return datasource.config_file

    async def import_config(self, config_json: str, name: str, market_id: UUID) -> tuple[bool, str, Optional[UUID]]:
        """
        导入配置创建新数据源。

        Args:
            config_json: 配置JSON字符串
            name: 数据源名称
            market_id: 市场ID

        Returns:
            (是否成功, 错误消息, 新数据源ID)
        """
        # 验证配置
        is_valid, error_msg, config_dict = validate_config_json(config_json)
        if not is_valid:
            return False, error_msg, None

        # 检查名称是否已存在
        result = await self.db.execute(
            select(DataSource).where(DataSource.name == name)
        )
        if result.scalar_one_or_none():
            return False, f"数据源名称'{name}'已存在", None

        # 创建数据源
        datasource = DataSource(
            name=name,
            market_id=market_id,
            interface=config_dict.get("type", "akshare"),
            description=config_dict.get("name", ""),
            config_schema={},
            config_file=config_json,
            config_version=config_dict.get("version", "1.0"),
            config_updated_at=datetime.now(timezone.utc),
            type=config_dict.get("type", "akshare"),
            is_active=True,
        )

        self.db.add(datasource)
        await self.db.commit()
        await self.db.refresh(datasource)

        return True, "", datasource.id

    async def apply_config(self, datasource_id: dict) -> dict:
        """
        获取解析后的配置字典供采集器使用。

        Args:
            datasource: 数据源对象或配置字典

        Returns:
            解析后的配置字典
        """
        # 如果传入的是对象
        if hasattr(datasource_id, 'config_file'):
            if datasource_id.config_file:
                return json.loads(datasource_id.config_file)
            return {}

        # 如果传入的已经是字典
        if isinstance(datasource_id, dict):
            return datasource_id

        return {}

    @staticmethod
    def get_default_config(config_type: str = "forex") -> str:
        """
        获取指定类型的默认配置。

        Args:
            config_type: 配置类型（forex/stock/futures）

        Returns:
            默认配置JSON字符串
        """
        if config_type == "forex":
            return get_default_forex_config()

        # 默认返回外汇配置
        return get_default_forex_config()


# 全局服务实例获取函数
_datasource_config_service: Optional[DatasourceConfigService] = None


def get_datasource_config_service(db: AsyncSession) -> DatasourceConfigService:
    """获取数据源配置服务实例。"""
    return DatasourceConfigService(db)