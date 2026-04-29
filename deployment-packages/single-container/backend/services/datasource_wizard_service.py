"""
数据源配置向导服务.

提供数据源配置向导的核心业务逻辑，包含：
- 会话管理
- API探测
- 端点发现
- 字段识别
- 测试采集

Author: FDAS Team
Created: 2026-04-21
"""

import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.datasource import DataSource
from app.models.datasource_wizard_session import DatasourceWizardSession
from app.models.market import Market

logger = logging.getLogger(__name__)


# 常用数据端点模式
COMMON_PATHS = [
    "/data",
    "/list",
    "/symbol",
    "/symbols",
    "/quotes",
    "/api/v1/data",
    "/api/v1/symbols",
    "/api/v1/list",
    "/api/market",
    "/api/stocks",
    "/api/forex",
    "/api/quote",
    "/kline",
    "/history",
    "/historical",
]

# 常用参数名
COMMON_PARAM_NAMES = [
    "symbol",
    "code",
    "market",
    "type",
    "symbol_code",
    "stock_code",
    "currency",
    "pair",
]

# 字段模式匹配
FIELD_PATTERNS = {
    "date": ["date", "time", "datetime", "trade_date", "timestamp", "day"],
    "open": ["open", "open_price", "openprice", "o"],
    "close": ["close", "close_price", "closeprice", "price", "last", "c"],
    "high": ["high", "high_price", "highprice", "h", "max"],
    "low": ["low", "low_price", "lowprice", "l", "min"],
    "volume": ["volume", "vol", "amount", "turnover", "v"],
}


class DatasourceWizardService:
    """数据源配置向导服务。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== 会话管理 ====================

    async def create_session(self, user_id: UUID) -> DatasourceWizardSession:
        """
        创建新的向导会话。

        Args:
            user_id: 用户ID

        Returns:
            新建的会话对象
        """
        session = DatasourceWizardSession(
            id=uuid4(),
            user_id=user_id,
            current_step=1,
            status="in_progress",
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session(self, session_id: UUID) -> Optional[DatasourceWizardSession]:
        """
        获取会话。

        Args:
            session_id: 会话ID

        Returns:
            会话对象或None
        """
        result = await self.db.execute(
            select(DatasourceWizardSession).where(
                DatasourceWizardSession.id == session_id
            )
        )
        return result.scalar_one_or_none()

    async def update_session_step(
        self,
        session_id: UUID,
        step: int,
        step_data: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        更新会话指定步骤的数据。

        Args:
            session_id: 会话ID
            step: 步骤号 (1-7)
            step_data: 步骤数据

        Returns:
            (是否成功, 错误消息)
        """
        session = await self.get_session(session_id)
        if not session:
            return False, "会话不存在"

        # 更新对应步骤的数据
        if step == 1:
            session.datasource_name = step_data.get("datasource_name")
            session.market_id = step_data.get("market_id")
        elif step == 2:
            session.api_base_url = step_data.get("api_base_url")
            session.api_method = step_data.get("api_method", "GET")
            session.api_timeout = step_data.get("api_timeout", 30)
            session.api_headers = step_data.get("api_headers")
        elif step == 3:
            session.selected_endpoint = step_data.get("selected_endpoint")
            session.available_endpoints = step_data.get("available_endpoints")
        elif step == 4:
            session.sample_data = step_data.get("sample_data")
        elif step == 5:
            session.field_mapping = step_data.get("field_mapping")
        elif step == 6:
            session.test_result = step_data.get("test_result")
        elif step == 7:
            session.status = step_data.get("status", "completed")

        session.current_step = step
        await self.db.commit()
        return True, ""

    # ==================== Step 2: API连接测试 ====================

    async def test_api_connection(
        self,
        base_url: str,
        method: str = "GET",
        timeout: int = 30,
        headers: Optional[Dict] = None,
    ) -> Tuple[bool, str, Dict]:
        """
        测试API连接。

        Args:
            base_url: API基础URL
            method: 请求方法
            timeout: 超时时间
            headers: 请求头

        Returns:
            (是否成功, 错误消息, 响应数据)
        """
        # 设置默认请求头
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
        }
        if headers:
            default_headers.update(headers)

        try:
            if method.upper() == "GET":
                response = requests.get(
                    base_url,
                    headers=default_headers,
                    timeout=timeout,
                )
            else:
                response = requests.post(
                    base_url,
                    headers=default_headers,
                    timeout=timeout,
                )

            # 检查HTTP状态
            if response.status_code >= 400:
                return False, f"HTTP错误: {response.status_code}", {}

            # 尝试解析JSON
            try:
                data = response.json()
                return True, "", data
            except json.JSONDecodeError:
                # 非JSON响应
                return True, "", {"raw": response.text[:500]}

        except requests.exceptions.Timeout:
            return False, "连接超时，请检查URL或超时时间", {}
        except requests.exceptions.ConnectionError:
            return False, "连接失败请检查网络或URL是否正确", {}
        except Exception as e:
            return False, f"请求失败: {str(e)}", {}

    # ==================== Step 3: 端点探测 ====================

    async def probe_endpoints(
        self,
        base_url: str,
        method: str = "GET",
        timeout: int = 30,
        headers: Optional[Dict] = None,
        test_params: Optional[Dict] = None,
    ) -> Tuple[bool, str, List[Dict]]:
        """
        探测可用端点。

        Args:
            base_url: API基础URL
            method: 请求方法
            timeout: 超时时间
            headers: 请求头
            test_params: 测试参数

        Returns:
            (是否成功, 错误消息, 可用端点列表)
        """
        endpoints_results = []

        # 设置默认请求头
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
        }
        if headers:
            default_headers.update(headers)

        # 如果没有测试参数，尝试常用参数
        if not test_params:
            test_params = {"symbol": "USDJPY", "code": "EURUSD"}

        discovered_endpoints = []

        # 尝试完整URL
        try:
            response = self._try_request(
                base_url, method, default_headers, timeout, test_params
            )
            if response:
                discovered_endpoints.append({
                    "path": base_url,
                    "description": "根路径",
                    "success": True,
                    "sample_count": self._count_records(response),
                })
        except:
            pass

        # 尝试常用路径
        for path in COMMON_PATHS:
            full_url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
            try:
                response = self._try_request(
                    full_url, method, default_headers, timeout, test_params
                )
                if response:
                    discovered_endpoints.append({
                        "path": full_url,
                        "description": self._describe_path(path),
                        "success": True,
                        "sample_count": self._count_records(response),
                    })
            except:
                continue

        if not discovered_endpoints:
            return False, "未发现可用端点，请手动输入完整API地址", []

        return True, "", discovered_endpoints

    def _try_request(
        self,
        url: str,
        method: str,
        headers: Dict,
        timeout: int,
        params: Dict,
    ) -> Optional[Dict]:
        """尝试发送请求。"""
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout, params=params)
            else:
                response = requests.post(url, headers=headers, timeout=timeout, json=params)

            if response.status_code < 400:
                try:
                    return response.json()
                except:
                    return {"raw": response.text[:200]}
        except:
            pass
        return None

    def _count_record(self, data: Any) -> int:
        """计算数据中的记录数。"""
        if isinstance(data, dict):
            # 常见结构: data, data.kline, records, result, items
            for key in ["data", "kline", "records", "result", "items"]:
                if key in data:
                    value = data[key]
                    if isinstance(value, list):
                        return len(value)
            return 1
        elif isinstance(data, list):
            return len(data)
        return 0

    def _describe_path(self, path: str) -> str:
        """描述路径用途。"""
        descriptions = {
            "/data": "数据接口",
            "/list": "列表接口",
            "/symbol": "标的信息",
            "/symbols": "标的信息",
            "/quotes": "行情数据",
            "/api/v1/data": "API数据v1",
            "/api/v1/symbols": "API标的对象",
            "/kline": "K线数据",
            "/history": "历史数据",
        }
        return descriptions.get(path, "数据接口")

    # ==================== Step 4: 数据预览 ====================

    async def fetch_sample_data(
        self,
        endpoint_url: str,
        method: str = "GET",
        timeout: int = 30,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Tuple[bool, str, List[Dict]]:
        """
        获取样本数据预览。

        Args:
            endpoint_url: 端点URL
            method: 请求方法
            timeout: 超时时间
            headers: 请求头
            params: 请求参数

        Returns:
            (是否成功, 错误消息, 样本数据列表)
        """
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
        }
        if headers:
            default_headers.update(headers)

        try:
            if method.upper() == "GET":
                response = requests.get(
                    endpoint_url, headers=default_headers, timeout=timeout, params=params
                )
            else:
                response = requests.post(
                    endpoint_url, headers=default_headers, timeout=timeout, json=params
                )

            if response.status_code >= 400:
                return False, f"请求失败: HTTP {response.status_code}", []

            # 解析数据
            try:
                data = response.json()
            except:
                return False, "无法解析返回数据为JSON", []

            # 提取数据列表
            records = self._extract_record_list(data)
            if not records:
                return False, "未获取到有效数据", []

            # 返回前10条
            return True, "", records[:10]

        except requests.exceptions.Timeout:
            return False, "请求超时", []
        except Exception as e:
            return False, f"获取数据失败: {str(e)}", []

    def _extract_record_list(self, data: Any) -> List[Dict]:
        """从响应中提取数据列表。"""
        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            # 常见结构
            for key in ["data", "kline", "records", "result", "items", "list"]:
                if key in data:
                    value = data[key]
                    if isinstance(value, list):
                        return value
                    if isinstance(value, dict):
                        # 可能嵌套
                        for sub_key in ["data", "kline", "records"]:
                            if sub_key in value and isinstance(value[sub_key], list):
                                return value[sub_key]

        return []

    # ==================== Step 5: 字段识别 ====================

    async def detect_field_mapping(
        self,
        sample_data: List[Dict],
    ) -> Tuple[bool, str, Dict]:
        """
        自动识别字段映射。

        Args:
            sample_data: 样本数据列表

        Returns:
            (是否成功, 错误消息, 字段映射建议)
        """
        if not sample_data:
            return False, "无样本数据", {}

        # 取第一条记录分析字段
        first_record = sample_data[0]
        if not isinstance(first_record, dict):
            return False, "数据格式不正确", {}

        detected_fields = {}
        record_keys = [k.lower() for k in first_record.keys()]

        # 匹配每个字段类型
        for field_type, patterns in FIELD_PATTERNS.items():
            for pattern in patterns:
                for key in record_keys:
                    if pattern in key:
                        detected_fields[field_type] = key
                        break
                if field_type in detected_fields:
                    break

        # 填充默认索引
        default_mapping = {
            "date_field": detected_fields.get("date", "date"),
            "open_field": detected_fields.get("open", "open"),
            "high_field": detected_fields.get("high", "high"),
            "low_field": detected_fields.get("low", "low"),
            "close_field": detected_fields.get("close", "close"),
            "volume_field": detected_fields.get("volume", "volume"),
            "response_root": "data",
        }

        return True, "", default_mapping

    # ==================== Step 6: 测试采集 ====================

    async def test_collection(
        self,
        config: Dict[str, Any],
        symbol_code: str = "TEST",
    ) -> Tuple[bool, str, int]:
        """
        测试采集功能（使用通用collect_daily方法）。

        Args:
            config: 完整配置字典
            symbol_code: 测试用标的代码

        Returns:
            (是否成功, 消息, 采集条数)
        """
        from app.collectors.akshare_collector import AKShareCollector

        try:
            # 创建采集器
            collector = AKShareCollector(config=config)

            # 使用最近30天
            from datetime import date, timedelta
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()

            # 尝试采集（使用通用入口）
            records = await collector.collect_daily(
                config=config,
                symbol=symbol_code,
                start_date=start_date,
                end_date=end_date,
            )

            if records and len(records) > 0:
                return True, f"成功采集 {len(records)} 条数据", len(records)
            else:
                return True, "连接成功但无数据返回", 0

        except Exception as e:
            return False, f"采集失败: {str(e)}", 0

    # ==================== Step 7: 保存数据源 ====================

    async def save_datasource(
        self,
        session_id: UUID,
    ) -> Tuple[bool, str, UUID]:
        """
        保存数据源到数据库。

        Args:
            session_id: 会话ID

        Returns:
            (是否成功, 错误消息, 数据源ID)
        """
        session = await self.get_session(session_id)
        if not session:
            return False, "会话不存在", None

        if session.status == "completed":
            return False, "数据源已创建", None

        # 生成配置JSON
        config_json = DatasourceWizardSession.generate_config_json(session)

        # 获取市场代码
        market_code = "forex"
        if session.market_id:
            result = await self.db.execute(
                select(Market).where(Market.id == session.market_id)
            )
            market = result.scalar_one_or_none()
            if market:
                market_code = market.code

        # 检查名称唯一
        result = await self.db.execute(
            select(DataSource).where(DataSource.name == session.datasource_name)
        )
        if result.scalar_one_or_none():
            return False, "数据源名称已存在请更换", None

        # 创建数据源
        datasource = DataSource(
            name=session.datasource_name,
            market_id=session.market_id,
            interface="custom",
            description=f"通过向导创建的数据源",
            config_schema={},
            config_file=config_json,
            config_version="1.0",
            config_updated_at=datetime.now(timezone.utc),
            type="custom",
            is_active=True,
        )
        self.db.add(datasource)
        await self.db.commit()
        await self.db.refresh(datasource)

        # 更新会话状态
        session.status = "completed"
        await self.db.commit()

        return True, "", datasource.id


def get_wizard_service(db: AsyncSession) -> DatasourceWizardService:
    """获取向导服务实例。"""
    return DatasourceWizardService(db)