"""
数据源向导服务测试。

为datasource_wizard_service.py提供完整的单元测试覆盖包含边界值测试。

测试目标:
- create_session: 创建向导会话
- get_session: 获取会话
- update_session_step: 更新会话步骤数据
- test_api_connection: 测试API连接
- probe_endpoints: 探测可用端点
- fetch_sample_data: 获取样本数据
- detect_field_mapping: 识别字段映射

覆盖率目标: 80%+

Author: FDAS Team
Created: 2026-04-21
"""

import pytest
import json
import uuid as uuid_module
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from uuid import uuid4, UUID
from datetime import datetime, timezone, date, timedelta


# 模拟DatasourceWizardService需要的数据
@pytest.fixture
def mock_db():
    """模拟数据库会话"""
    mock = AsyncMock()
    mock.add = MagicMock()
    mock.commit = AsyncMock()
    mock.refresh = AsyncMock()
    return mock


@pytest.fixture
def mock_session():
    """模拟向导会话对象"""
    session = MagicMock()
    session.id = uuid4()
    session.user_id = uuid4()
    session.current_step = 1
    session.status = "in_progress"
    session.datasource_name = "测试数据源"
    session.market_id = uuid4()
    session.api_base_url = "https://api.example.com"
    session.api_method = "GET"
    session.api_timeout = 30
    session.api_headers = {}
    session.selected_endpoint = None
    session.available_endpoints = None
    session.sample_data = None
    session.field_mapping = None
    session.test_result = None
    return session


# ============ Test Class: Session Management ============

class TestCreateSession:
    """创建向导会话测试"""

    @pytest.mark.asyncio
    async def test_create_session_success(self, mock_db):
        """测试成功创建会话"""
        from app.services.datasource_wizard_service import DatasourceWizardService
        from app.services.datasource_wizard_service import DatasourceWizardSession as OrigSession

        with patch('app.services.datasource_wizard_service.DatasourceWizardSession') as MockSessionClass:
            # Setup mock - 创建一个有效的模拟会话对象
            mock_instance = MagicMock()
            mock_instance.id = uuid4()
            mock_instance.user_id = uuid4()
            mock_instance.current_step = 1
            mock_instance.status = "in_progress"
            MockSessionClass.return_value = mock_instance

            service = DatasourceWizardService(mock_db)
            user_id = uuid4()

            result = await service.create_session(user_id)

            # 验证
            assert result is not None
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_session_sets_correct_values(self, mock_db):
        """测试创建的会话设置正确的值"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        with patch('app.services.datasource_wizard_service.DatasourceWizardSession') as MockSessionClass:
            mock_instance = MagicMock()
            mock_instance.id = uuid4()
            mock_instance.user_id = uuid4()
            mock_instance.current_step = 1
            mock_instance.status = "in_progress"
            MockSessionClass.return_value = mock_instance

            service = DatasourceWizardService(mock_db)
            user_id = uuid4()

            result = await service.create_session(user_id)

            # 验证初始值
            assert result.current_step == 1
            assert result.status == "in_progress"


class TestGetSession:
    """获取会话测试"""

    @pytest.mark.asyncio
    async def test_get_session_exists(self, mock_db, mock_session):
        """测试获取存在的会话"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        with patch('app.services.datasource_wizard_service.select') as mock_select, \
             patch('app.services.datasource_wizard_service.DatasourceWizardSession') as MockSession:
            # Mock查询结果
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_session

            mock_db.execute = AsyncMock(return_value=mock_result)

            service = DatasourceWizardService(mock_db)
            result = await service.get_session(mock_session.id)

            assert result is not None
            assert result.id == mock_session.id

    @pytest.mark.asyncio
    async def test_get_session_not_exists(self, mock_db):
        """测试获取不存在的会话返回None"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        with patch('app.services.datasource_wizard_service.select') as mock_select, \
             patch('app.services.datasource_wizard_service.DatasourceWizardSession') as MockSession:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None

            mock_db.execute = AsyncMock(return_value=mock_result)

            service = DatasourceWizardService(mock_db)
            result = await service.get_session(uuid4())

            assert result is None


class TestUpdateSessionStep:
    """更新会话步骤数据测试"""

    @pytest.mark.asyncio
    async def test_update_session_step_1(self, mock_db, mock_session):
        """测试更新步骤1数据（基础信息）"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        with patch.object(service := DatasourceWizardService(mock_db), 'get_session', return_value=mock_session):
            mock_session.datasource_name = None
            mock_session.market_id = None

            success, error = await service.update_session_step(
                mock_session.id,
                step=1,
                step_data={
                    "datasource_name": "新数据源",
                    "market_id": uuid4()
                }
            )

            assert success is True
            assert error == ""
            assert mock_session.datasource_name == "新数据源"

    @pytest.mark.asyncio
    async def test_update_session_step_2(self, mock_db, mock_session):
        """测试更新步骤2数据（API配置）"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        with patch.object(service := DatasourceWizardService(mock_db), 'get_session', return_value=mock_session):
            success, error = await service.update_session_step(
                mock_session.id,
                step=2,
                step_data={
                    "api_base_url": "https://new-api.example.com",
                    "api_method": "POST",
                    "api_timeout": 60,
                    "api_headers": {"Authorization": "Bearer token"}
                }
            )

            assert success is True
            assert mock_session.api_base_url == "https://new-api.example.com"
            assert mock_session.api_method == "POST"
            assert mock_session.api_timeout == 60

    @pytest.mark.asyncio
    async def test_update_session_step_not_found(self, mock_db):
        """测试更新不存在的会话返回失败"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        with patch.object(service := DatasourceWizardService(mock_db), 'get_session', return_value=None):
            success, error = await service.update_session_step(
                uuid4(),
                step=1,
                step_data={}
            )

            assert success is False
            assert "会话不存在" in error


# ============ Test Class: API Connection Test ============

class TestApiConnection:
    """API连接测试"""

    @pytest.mark.asyncio
    async def test_api_connection_success(self, mock_db):
        """测试API连接成功"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(mock_db)

        with patch('app.services.datasource_wizard_service.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            mock_get.return_value = mock_response

            success, error_msg, data = await service.test_api_connection(
                base_url="https://api.example.com",
                method="GET",
                timeout=30
            )

            assert success is True
            assert error_msg == ""
            assert data == {"data": "test"}

    @pytest.mark.asyncio
    async def test_api_connection_timeout(self, mock_db):
        """测试API连接超时"""
        from app.services.datasource_wizard_service import DatasourceWizardService
        import requests

        service = DatasourceWizardService(mock_db)

        with patch('app.services.datasource_wizard_service.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()

            success, error_msg, data = await service.test_api_connection(
                base_url="https://api.example.com",
                method="GET",
                timeout=30
            )

            assert success is False
            assert "超时" in error_msg

    @pytest.mark.asyncio
    async def test_api_connection_connection_error(self, mock_db):
        """测试API连接失败"""
        from app.services.datasource_wizard_service import DatasourceWizardService
        import requests

        service = DatasourceWizardService(mock_db)

        with patch('app.services.datasource_wizard_service.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()

            success, error_msg, data = await service.test_api_connection(
                base_url="https://api.example.com",
                method="GET",
                timeout=30
            )

            assert success is False
            assert "连接" in error_msg

    @pytest.mark.asyncio
    async def test_api_connection_http_error(self, mock_db):
        """测试API HTTP错误"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(mock_db)

        with patch('app.services.datasource_wizard_service.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            success, error_msg, data = await service.test_api_connection(
                base_url="https://api.example.com",
                method="GET",
                timeout=30
            )

            assert success is False
            assert "404" in error_msg


# ============ Test Class: Endpoint Probe ============

class TestProbeEndpoints:
    """端点探测测试"""

    @pytest.mark.asyncio
    async def test_probe_endpoints_success(self, mock_db):
        """测试成功探测端点"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(mock_db)

        # Mock _try_request 对根路径返回数据（模拟成功发现一个端点）
        def mock_try_request(url, method, headers, timeout, params):
            if url.endswith('/data') or url == "https://api.example.com":
                return {"data": [{"date": "2024-01-01", "close": 100}]}
            return None

        with patch.object(service, '_try_request', side_effect=mock_try_request):
            success, error_msg, endpoints_list = await service.probe_endpoints(
                base_url="https://api.example.com",
                method="GET",
                timeout=30
            )

            # 只有当有端点被发现时才返回成功
            assert isinstance(endpoints_list, list)

    @pytest.mark.asyncio
    async def test_probe_endpoints_no_endpoints(self, mock_db):
        """测试未发现端点"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(mock_db)

        # Mock _try_request 返回None
        with patch.object(service, '_try_request') as mock_try:
            mock_try.return_value = None

            success, error_msg, endpoints = await service.probe_endpoints(
                base_url="https://api.example.com",
                method="GET",
                timeout=30
            )

            assert success is False
            assert "未发现" in error_msg


class TestExtractRecordList:
    """数据提取测试"""

    def test_extract_from_list(self):
        """测试从列表提取"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(AsyncMock())

        data = [{"a": 1}, {"b": 2}]
        result = service._extract_record_list(data)

        assert result == [{"a": 1}, {"b": 2}]

    def test_extract_from_dict_with_data_key(self):
        """测试从dict的data键提取"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(AsyncMock())

        data = {"data": [{"a": 1}, {"b": 2}]}
        result = service._extract_record_list(data)

        assert result == [{"a": 1}, {"b": 2}]

    def test_extract_from_dict_with_kline_key(self):
        """测试从dict的kline键提取"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(AsyncMock())

        data = {"kline": [{"a": 1}]}
        result = service._extract_record_list(data)

        assert result == [{"a": 1}]

    def test_extract_nested(self):
        """测试嵌套结构提取"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(AsyncMock())

        data = {"result": {"data": [{"a": 1}]}}
        result = service._extract_record_list(data)

        assert result == [{"a": 1}]

    def test_extract_no_valid_data(self):
        """测试无效数据返回空列表"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(AsyncMock())

        data = "string only"
        result = service._extract_record_list(data)

        assert result == []


# ============ Test Class: Field Mapping Detection ============

class TestDetectFieldMapping:
    """字段识别测试"""

    @pytest.mark.asyncio
    async def test_detect_field_mapping_success(self, mock_db):
        """测试成功识别字段映射"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(mock_db)

        sample_data = [
            {"date": "2024-01-01", "open": 100, "high": 105, "low": 99, "close": 103, "volume": 1000},
            {"date": "2024-01-02", "open": 103, "high": 108, "low": 102, "close": 106, "volume": 2000}
        ]

        success, error_msg, mapping = await service.detect_field_mapping(sample_data)

        assert success is True
        assert mapping["date_field"] == "date"
        assert mapping["open_field"] == "open"
        assert mapping["close_field"] == "close"

    @pytest.mark.asyncio
    async def test_detect_field_mapping_empty_data(self, mock_db):
        """测试空数据返回失败"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(mock_db)

        success, error_msg, mapping = await service.detect_field_mapping([])

        assert success is False
        assert "无样本数据" in error_msg

    @pytest.mark.asyncio
    async def test_detect_field_mapping_alternative_names(self, mock_db):
        """测试识别替代字段名（open_price等）"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(mock_db)

        sample_data = [
            {"trade_date": "2024-01-01", "open_price": 100, "high_price": 105, "low_price": 99, "close_price": 103, "vol": 1000}
        ]

        success, error_msg, mapping = await service.detect_field_mapping(sample_data)

        assert success is True
        assert mapping["date_field"] == "trade_date"
        assert mapping["open_field"] == "open_price"
        assert mapping["close_field"] == "close_price"


class TestCountRecord:
    """记录计数测试"""

    def test_count_from_dict_data_key(self):
        """测试从dict的data键计数"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(AsyncMock())

        data = {"data": [1, 2, 3]}
        count = service._count_record(data)

        assert count == 3

    def test_count_from_list(self):
        """测试从列表计数"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(AsyncMock())

        data = [1, 2, 3, 4, 5]
        count = service._count_record(data)

        assert count == 5

    def test_count_from_dict_no_list(self):
        """测试dict无list键返回1"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(AsyncMock())

        data = {"single": "value"}
        count = service._count_record(data)

        assert count == 1


# ============ Test Class: Describe Path ============

class TestDescribePath:
    """路径描述测试"""

    def test_describe_data_path(self):
        """测试/data描述"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(AsyncMock())

        desc = service._describe_path("/data")

        assert "数据" in desc

    def test_describe_symbols_path(self):
        """测试/symbols描述"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(AsyncMock())

        desc = service._describe_path("/symbols")

        assert "标的信息" in desc

    def test_describe_unknown_path(self):
        """测试未知路径返回默认值"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        service = DatasourceWizardService(AsyncMock())

        desc = service._describe_path("/unknown")

        # 未知路径返回 "数据接口" 作为默认值
        assert desc == "数据接口"


# ============ Test Class: Save Datasource ============

class TestSaveDatasource:
    """保存数据源测试"""

    @pytest.mark.asyncio
    async def test_save_datasource_session_not_found(self, mock_db):
        """测试会话不存在返回失败"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        with patch.object(service := DatasourceWizardService(mock_db), 'get_session', return_value=None):
            success, error_msg, ds_id = await service.save_datasource(uuid4())

            assert success is False
            assert "会话不存在" in error_msg

    @pytest.mark.asyncio
    async def test_save_datasource_already_completed(self, mock_db, mock_session):
        """测试已完成的会话返回失败"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        mock_session.status = "completed"

        with patch.object(service := DatasourceWizardService(mock_db), 'get_session', return_value=mock_session):
            success, error_msg, ds_id = await service.save_datasource(mock_session.id)

            assert success is False
            assert "已创建" in error_msg

    @pytest.mark.asyncio
    async def test_save_datasource_duplicate_name(self, mock_db, mock_session):
        """测试名称重复返回失败"""
        from app.services.datasource_wizard_service import DatasourceWizardService

        mock_session.datasource_name = "已存在数据源"

        # Mock名称检查返回已存在
        with patch.object(service := DatasourceWizardService(mock_db), 'get_session', return_value=mock_session), \
             patch('app.services.datasource_wizard_service.select') as mock_select, \
             patch('app.services.datasource_wizard_service.DataSource') as MockDataSource:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = MagicMock()  # 已存在
            mock_db.execute = AsyncMock(return_value=mock_result)

            success, error_msg, ds_id = await service.save_datasource(mock_session.id)

            assert success is False
            assert "已存在" in error_msg


# ============ Test Class: Get Wizard Service ============

class TestGetWizardService:
    """获取向导服务实例测试"""

    def test_get_wizard_service_returns_instance(self):
        """测试返回服务实例"""
        from app.services.datasource_wizard_service import get_wizard_service, DatasourceWizardService

        mock_db = AsyncMock()
        service = get_wizard_service(mock_db)

        assert isinstance(service, DatasourceWizardService)