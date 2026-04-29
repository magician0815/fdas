"""
图表模板服务.

保存、加载、分享图表配置模板.
支持均线配置、指标参数、画线工具、主题设置等.

Author: FDAS Team
Created: 2026-04-14
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timezone
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.user_chart_setting import UserChartSetting

logger = logging.getLogger(__name__)


class ChartTemplate:
    """图表模板数据结构."""

    def __init__(
        self,
        template_id: str,
        name: str,
        description: str,
        config: Dict[str, Any],
        is_public: bool,
        creator_id: UUID,
        created_at: datetime,
        updated_at: datetime
    ):
        self.template_id = template_id
        self.name = name
        self.description = description
        self.config = config
        self.is_public = is_public
        self.creator_id = creator_id
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "config": self.config,
            "is_public": self.is_public,
            "creator_id": str(self.creator_id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class ChartTemplateService:
    """图表模板服务类."""

    def __init__(self):
        # 模板配置键名
        self.TEMPLATE_KEY = "template"

    async def save_template(
        self,
        db: AsyncSession,
        user_id: UUID,
        template_name: str,
        template_config: Dict[str, Any],
        description: str = "",
        is_public: bool = False
    ) -> ChartTemplate:
        """
        保存图表模板.

        Args:
            db: 数据库会话
            user_id: 用户ID
            template_name: 模板名称
            template_config: 模板配置（包含均线、指标、画线、主题等）
            description: 模板描述
            is_public: 是否公开分享

        Returns:
            保存的模板对象
        """
        template_id = f"template_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{str(user_id)[:8]}"

        # 创建配置记录
        setting = UserChartSetting(
            user_id=user_id,
            setting_type="chart_template",
            setting_key=template_id,
            setting_value={
                "name": template_name,
                "description": description,
                "config": template_config,
                "is_public": is_public,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        )

        db.add(setting)
        await db.commit()
        await db.refresh(setting)

        logger.info(f"用户 {user_id} 保存模板: {template_name}")

        return ChartTemplate(
            template_id=template_id,
            name=template_name,
            description=description,
            config=template_config,
            is_public=is_public,
            creator_id=user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    async def load_template(
        self,
        db: AsyncSession,
        template_id: str
    ) -> Optional[ChartTemplate]:
        """
        加载图表模板.

        Args:
            db: 数据库会话
            template_id: 模板ID

        Returns:
            模板对象，如果不存在则返回None
        """
        result = await db.execute(
            select(UserChartSetting).where(
                and_(
                    UserChartSetting.setting_type == "chart_template",
                    UserChartSetting.setting_key == template_id
                )
            )
        )

        setting = result.scalar_one_or_none()

        if not setting:
            return None

        data = setting.setting_value

        return ChartTemplate(
            template_id=template_id,
            name=data.get("name", "未命名模板"),
            description=data.get("description", ""),
            config=data.get("config", {}),
            is_public=data.get("is_public", False),
            creator_id=setting.user_id,
            created_at=datetime.fromisoformat(data.get("created_at")),
            updated_at=datetime.fromisoformat(data.get("updated_at"))
        )

    async def list_user_templates(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> List[ChartTemplate]:
        """
        获取用户的模板列表.

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            用户模板列表
        """
        result = await db.execute(
            select(UserChartSetting).where(
                and_(
                    UserChartSetting.user_id == user_id,
                    UserChartSetting.setting_type == "chart_template"
                )
            )
        )

        settings = result.scalars().all()

        templates = []
        for setting in settings:
            data = setting.setting_value
            templates.append(ChartTemplate(
                template_id=setting.setting_key,
                name=data.get("name", "未命名模板"),
                description=data.get("description", ""),
                config=data.get("config", {}),
                is_public=data.get("is_public", False),
                creator_id=setting.user_id,
                created_at=datetime.fromisoformat(data.get("created_at")),
                updated_at=datetime.fromisoformat(data.get("updated_at"))
            ))

        return templates

    async def list_public_templates(
        self,
        db: AsyncSession,
        limit: int = 20
    ) -> List[ChartTemplate]:
        """
        获取公开模板列表.

        Args:
            db: 数据库会话
            limit: 返回数量限制

        Returns:
            公开模板列表
        """
        # 查询所有公开模板
        result = await db.execute(
            select(UserChartSetting).where(
                and_(
                    UserChartSetting.setting_type == "chart_template"
                )
            ).limit(limit)
        )

        settings = result.scalars().all()

        templates = []
        for setting in settings:
            data = setting.setting_value
            if data.get("is_public", False):
                templates.append(ChartTemplate(
                    template_id=setting.setting_key,
                    name=data.get("name", "未命名模板"),
                    description=data.get("description", ""),
                    config=data.get("config", {}),
                    is_public=True,
                    creator_id=setting.user_id,
                    created_at=datetime.fromisoformat(data.get("created_at")),
                    updated_at=datetime.fromisoformat(data.get("updated_at"))
                ))

        return templates

    async def update_template(
        self,
        db: AsyncSession,
        user_id: UUID,
        template_id: str,
        updates: Dict[str, Any]
    ) -> Optional[ChartTemplate]:
        """
        更新模板.

        Args:
            db: 数据库会话
            user_id: 用户ID
            template_id: 模板ID
            updates: 更新内容

        Returns:
            更新后的模板对象
        """
        result = await db.execute(
            select(UserChartSetting).where(
                and_(
                    UserChartSetting.user_id == user_id,
                    UserChartSetting.setting_type == "chart_template",
                    UserChartSetting.setting_key == template_id
                )
            )
        )

        setting = result.scalar_one_or_none()

        if not setting:
            return None

        # 更新配置
        current_value = setting.setting_value
        for key, value in updates.items():
            if key == "config":
                current_value["config"] = value
            elif key == "name":
                current_value["name"] = value
            elif key == "description":
                current_value["description"] = value
            elif key == "is_public":
                current_value["is_public"] = value

        current_value["updated_at"] = datetime.now(timezone.utc).isoformat()
        setting.setting_value = current_value

        await db.commit()
        await db.refresh(setting)

        logger.info(f"用户 {user_id} 更新模板: {template_id}")

        return await self.load_template(db, template_id)

    async def delete_template(
        self,
        db: AsyncSession,
        user_id: UUID,
        template_id: str
    ) -> bool:
        """
        删除模板.

        Args:
            db: 数据库会话
            user_id: 用户ID
            template_id: 模板ID

        Returns:
            是否删除成功
        """
        result = await db.execute(
            select(UserChartSetting).where(
                and_(
                    UserChartSetting.user_id == user_id,
                    UserChartSetting.setting_type == "chart_template",
                    UserChartSetting.setting_key == template_id
                )
            )
        )

        setting = result.scalar_one_or_none()

        if not setting:
            return False

        await db.delete(setting)
        await db.commit()

        logger.info(f"用户 {user_id} 删除模板: {template_id}")

        return True

    async def apply_template_to_chart(
        self,
        db: AsyncSession,
        user_id: UUID,
        template_id: str,
        symbol_id: str
    ) -> bool:
        """
        应用模板到指定标的图表.

        Args:
            db: 数据库会话
            user_id: 用户ID
            template_id: 模板ID
            symbol_id: 标的ID

        Returns:
            是否应用成功
        """
        template = await self.load_template(db, template_id)

        if not template:
            return False

        # 保存当前标的的图表配置
        config_key = f"chart_config_{symbol_id}"

        result = await db.execute(
            select(UserChartSetting).where(
                and_(
                    UserChartSetting.user_id == user_id,
                    UserChartSetting.setting_type == "chart_config",
                    UserChartSetting.setting_key == config_key
                )
            )
        )

        setting = result.scalar_one_or_none()

        if setting:
            # 更新现有配置
            setting.setting_value = template.config
        else:
            # 创建新配置
            setting = UserChartSetting(
                user_id=user_id,
                setting_type="chart_config",
                setting_key=config_key,
                setting_value=template.config
            )
            db.add(setting)

        await db.commit()

        logger.info(f"用户 {user_id} 应用模板 {template_id} 到标的 {symbol_id}")

        return True

    def generate_share_link(self, template_id: str, base_url: str = "") -> str:
        """
        生成模板分享链接.

        Args:
            template_id: 模板ID
            base_url: 基础URL

        Returns:
            分享链接
        """
        return f"{base_url}/chart/template/{template_id}"


# 导出服务实例
chart_template_service = ChartTemplateService()