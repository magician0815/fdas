"""
数据源配置向导会话模型.

存储用户在配置向导过程中的临时数据和进度.

Author: FDAS Team
Created: 2026-04-21
"""

from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.core.database import Base


class DatasourceWizardSession(Base):
    """
    数据源配置向导会话表.

    用于存储用户在数据源配置向导过程中的临时数据,
    支持用户分步骤配置并在任意步骤返回修改.
    """
    __tablename__ = "datasource_wizard_sessions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, comment="会话唯一标识ID")
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, comment="创建用户ID")

    # 当前步骤 (1-7)
    current_step = Column(Integer, nullable=False, default=1, comment="当前步骤(1-7)")

    # 步骤1: 基础信息
    datasource_name = Column(String(100), nullable=True, comment="数据源名称")
    market_id = Column(PGUUID(as_uuid=True), ForeignKey("markets.id"), nullable=True, comment="市场ID")

    # 步骤2: API配置
    api_base_url = Column(Text, nullable=True, comment="API基础URL")
    api_method = Column(String(10), nullable=True, comment="请求方法(GET/POST)")
    api_timeout = Column(Integer, nullable=True, comment="超时时间(秒)")
    api_headers = Column(JSON, nullable=True, comment="请求头JSON")

    # 步骤3: 端点配置
    selected_endpoint = Column(Text, nullable=True, comment="选中的数据端点路径")
    available_endpoints = Column(JSON, nullable=True, comment="发现的可用端点列表")

    # 步骤4: 数据预览
    sample_data = Column(JSON, nullable=True, comment="样本数据预览")

    # 步骤5: 字段映射
    field_mapping = Column(JSON, nullable=True, comment="字段映射配置")

    # 步骤6: 测试采集结果
    test_result = Column(JSON, nullable=True, comment="测试采集结果")

    # 会话状态
    status = Column(String(20), nullable=False, default="in_progress", comment="会话状态(in_progress/completed/failed)")
    error_message = Column(Text, nullable=True, comment="错误信息")

    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), comment="更新时间")

    def to_step_data(self, step: int) -> Dict[str, Any]:
        """
        获取指定步骤的数据.

        Args:
            step: 步骤号 (1-7)

        Returns:
            该步骤的数据字典
        """
        step_data_map = {
            1: {
                "datasource_name": self.datasource_name,
                "market_id": self.market_id,
            },
            2: {
                "api_base_url": self.api_base_url,
                "api_method": self.api_method,
                "api_timeout": self.api_timeout,
                "api_headers": self.api_headers,
            },
            3: {
                "selected_endpoint": self.selected_endpoint,
                "available_endpoints": self.available_endpoints,
            },
            4: {
                "sample_data": self.sample_data,
            },
            5: {
                "field_mapping": self.field_mapping,
            },
            6: {
                "test_result": self.test_result,
            },
            7: {
                "completed": self.status == "completed",
            },
        }
        return step_data_map.get(step, {})

    @classmethod
    def generate_config_json(cls, session: "DatasourceWizardSession") -> str:
        """
        根据会话数据生成配置JSON.

        Args:
            session: 向导会话对象

        Returns:
            配置JSON字符串
        """
        import json

        config = {
            "version": "1.0",
            "name": session.datasource_name or "未命名数据源",
            "type": "custom",
            "market": "forex",  # 可从market_id查询获取
            "api": {
                "base_url": session.api_base_url,
                "method": session.api_method or "GET",
                "timeout": session.api_timeout or 30,
            },
            "headers": session.api_headers or {},
            "data_parser": session.field_mapping or {},
        }

        return json.dumps(config, ensure_ascii=False, indent=2)