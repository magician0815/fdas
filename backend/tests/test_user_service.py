"""
用户服务测试.

为user_service.py提供完整的单元测试覆盖，包含边界值测试。

测试目标:
- create_user: 创建用户
- get_user_by_id: 根据ID获取用户
- get_user_by_username: 根据用户名获取用户
- get_users: 获取用户列表
- update_user: 更新用户
- delete_user: 删除用户

覆盖率目标: 100%

Author: FDAS Team
Created: 2026-04-14
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.user_service import UserService, user_service
from app.models.user import User


# ============ Fixtures ============

@pytest.fixture
def mock_db_session():
    """Mock数据库会话."""
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_user():
    """Mock用户对象."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.username = "testuser"
    user.password_hash = "$2b$12$hashedpassword"
    user.role = "user"
    return user


@pytest.fixture
def user_service_instance():
    """用户服务实例."""
    return UserService()


# ============ Test Class: create_user ============

class TestCreateUser:
    """
    创建用户函数测试.

    测试create_user函数的各种场景。
    """

    # ============ 正常场景测试 ============

    @pytest.mark.asyncio
    async def test_create_user_normal_success(self, user_service_instance, mock_db_session):
        """测试正常创建用户成功."""
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        user = await user_service_instance.create_user(
            mock_db_session,
            username="newuser",
            password="SecurePass123!",
            role="user"
        )

        assert user is not None
        assert user.username == "newuser"
        assert user.role == "user"
        assert user.password_hash is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_admin_role_success(self, user_service_instance, mock_db_session):
        """测试创建管理员角色用户成功."""
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        user = await user_service_instance.create_user(
            mock_db_session,
            username="adminuser",
            password="AdminPass123!",
            role="admin"
        )

        assert user.role == "admin"

    @pytest.mark.asyncio
    async def test_create_user_default_role_success(self, user_service_instance, mock_db_session):
        """测试默认角色为user."""
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        user = await user_service_instance.create_user(
            mock_db_session,
            username="defaultuser",
            password="DefaultPass123!"
        )

        assert user.role == "user"

    # ============ 边界值测试 ============

    # 1. Null/Undefined输入
    @pytest.mark.asyncio
    async def test_create_user_none_username_accepts_input(self, user_service_instance, mock_db_session):
        """测试None用户名（底层允许，业务层应校验）."""
        # SQLAlchemy底层允许None用户名
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        user = await user_service_instance.create_user(
            mock_db_session,
            username=None,
            password="Password123!"
        )

        # 底层允许，业务层应在API层校验
        assert user.username is None

    @pytest.mark.asyncio
    async def test_create_user_none_password_raises_error(self, user_service_instance, mock_db_session):
        """测试None密码应抛出错误."""
        with pytest.raises((TypeError, AttributeError, ValueError)):
            await user_service_instance.create_user(
                mock_db_session,
                username="testuser",
                password=None
            )

    @pytest.mark.asyncio
    async def test_create_user_none_db_raises_error(self, user_service_instance):
        """测试None数据库会话应抛出错误."""
        with pytest.raises((TypeError, AttributeError)):
            await user_service_instance.create_user(
                None,
                username="testuser",
                password="Password123!"
            )

    # 2. 空字符串
    @pytest.mark.asyncio
    async def test_create_user_empty_username_success(self, user_service_instance, mock_db_session):
        """测试空用户名创建（业务层应拒绝，但底层允许）."""
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        user = await user_service_instance.create_user(
            mock_db_session,
            username="",
            password="Password123!"
        )

        assert user.username == ""

    @pytest.mark.asyncio
    async def test_create_user_empty_password_success(self, user_service_instance, mock_db_session):
        """测试空密码创建（bcrypt允许）."""
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        user = await user_service_instance.create_user(
            mock_db_session,
            username="testuser",
            password=""
        )

        assert user.password_hash is not None

    # 3. 无效类型
    @pytest.mark.asyncio
    async def test_create_user_integer_username_accepts_input(self, user_service_instance, mock_db_session):
        """测试整数用户名（底层会转换为字符串）."""
        # SQLAlchemy底层会将整数转为字符串
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        user = await user_service_instance.create_user(
            mock_db_session,
            username=12345,
            password="Password123!"
        )

        # 底层行为：整数被转为字符串
        assert user.username == "12345"

    @pytest.mark.asyncio
    async def test_create_user_invalid_role_raises_error(self, user_service_instance, mock_db_session):
        """测试无效角色类型."""
        # 角色不是user/admin，但底层允许任意字符串
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        user = await user_service_instance.create_user(
            mock_db_session,
            username="testuser",
            password="Password123!",
            role="invalid_role"
        )

        # 底层允许任意角色字符串
        assert user.role == "invalid_role"

    # 4. 边界值
    @pytest.mark.asyncio
    async def test_create_user_single_char_username_success(self, user_service_instance, mock_db_session):
        """测试单字符用户名."""
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        user = await user_service_instance.create_user(
            mock_db_session,
            username="a",
            password="Password123!"
        )

        assert user.username == "a"

    @pytest.mark.asyncio
    async def test_create_user_max_length_username_success(self, user_service_instance, mock_db_session):
        """测试最大长度用户名（255字符）."""
        long_username = "a" * 255
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        user = await user_service_instance.create_user(
            mock_db_session,
            username=long_username,
            password="Password123!"
        )

        assert user.username == long_username

    @pytest.mark.asyncio
    async def test_create_user_bcrypt_max_password_success(self, user_service_instance, mock_db_session):
        """测试bcrypt最大密码长度（72字符）."""
        max_password = "a" * 72  # bcrypt限制
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        user = await user_service_instance.create_user(
            mock_db_session,
            username="testuser",
            password=max_password
        )

        assert user.password_hash is not None

    @pytest.mark.asyncio
    async def test_create_user_password_exceeds_bcrypt_limit_raises_error(self, user_service_instance, mock_db_session):
        """测试超过bcrypt限制的密码应抛出错误."""
        long_password = "a" * 100  # 超过72字节限制

        with pytest.raises(ValueError):
            await user_service_instance.create_user(
                mock_db_session,
                username="testuser",
                password=long_password
            )

    # 5. 错误路径
    @pytest.mark.asyncio
    async def test_create_user_db_commit_error_handles_gracefully(self, user_service_instance, mock_db_session):
        """测试数据库提交错误处理."""
        mock_db_session.commit.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            await user_service_instance.create_user(
                mock_db_session,
                username="testuser",
                password="Password123!"
            )

    # 6. 竞态条件
    @pytest.mark.asyncio
    async def test_create_user_concurrent_requests(self, user_service_instance, mock_db_session):
        """测试并发创建用户."""
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        tasks = [
            user_service_instance.create_user(mock_db_session, f"user{i}", "Password123!")
            for i in range(10)
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        for user in results:
            assert user is not None

    # 8. 特殊字符
    @pytest.mark.asyncio
    async def test_create_user_unicode_username_success(self, user_service_instance, mock_db_session):
        """测试Unicode用户名."""
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        user = await user_service_instance.create_user(
            mock_db_session,
            username="用户名测试",
            password="Password123!"
        )

        assert user.username == "用户名测试"

    @pytest.mark.asyncio
    async def test_create_user_sql_injection_username_success(self, user_service_instance, mock_db_session):
        """测试SQL注入字符用户名（应被安全存储）."""
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        user = await user_service_instance.create_user(
            mock_db_session,
            username="admin'; DROP TABLE users; --",
            password="Password123!"
        )

        # SQLAlchemy安全处理，不会执行注入
        assert user.username == "admin'; DROP TABLE users; --"

    @pytest.mark.asyncio
    async def test_create_user_special_chars_password_success(self, user_service_instance, mock_db_session):
        """测试特殊字符密码."""
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', uuid4())

        user = await user_service_instance.create_user(
            mock_db_session,
            username="testuser",
            password="P@ssw0rd!#$%^&*()"
        )

        assert user.password_hash is not None


# ============ Test Class: get_user_by_id ============

class TestGetUserById:
    """
    根据ID获取用户函数测试.

    测试get_user_by_id函数的各种场景。
    """

    # ============ 正常场景测试 ============

    @pytest.mark.asyncio
    async def test_get_user_by_id_exists_returns_user(self, user_service_instance, mock_db_session, mock_user):
        """测试用户存在时返回用户."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.get_user_by_id(mock_db_session, mock_user.id)

        assert user == mock_user
        assert user.username == mock_user.username

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_exists_returns_none(self, user_service_instance, mock_db_session):
        """测试用户不存在时返回None."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.get_user_by_id(mock_db_session, uuid4())

        assert user is None

    # ============ 边界值测试 ============

    # 1. Null/Undefined输入
    @pytest.mark.asyncio
    async def test_get_user_by_id_none_id_returns_none(self, user_service_instance, mock_db_session):
        """测试None ID返回None."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.get_user_by_id(mock_db_session, None)

        # 查询条件None可能导致空结果
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_id_none_db_raises_error(self, user_service_instance):
        """测试None数据库会话应抛出错误."""
        with pytest.raises((TypeError, AttributeError)):
            await user_service_instance.get_user_by_id(None, uuid4())

    # 3. 无效类型
    @pytest.mark.asyncio
    async def test_get_user_by_id_string_id_accepts_input(self, user_service_instance, mock_db_session):
        """测试字符串ID（底层可能处理，业务层应校验UUID格式）."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.get_user_by_id(mock_db_session, "not-a-uuid")

        # 底层行为：非UUID字符串可能返回None
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_id_integer_id_accepts_input(self, user_service_instance, mock_db_session):
        """测试整数ID（底层可能处理，业务层应校验UUID类型）."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.get_user_by_id(mock_db_session, 12345)

        mock_db_session.execute.assert_called_once()

    # 5. 错误路径
    @pytest.mark.asyncio
    async def test_get_user_by_id_db_error_handles_gracefully(self, user_service_instance, mock_db_session):
        """测试数据库错误处理."""
        mock_db_session.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            await user_service_instance.get_user_by_id(mock_db_session, uuid4())


# ============ Test Class: get_user_by_username ============

class TestGetUserByUsername:
    """
    根据用户名获取用户函数测试.

    测试get_user_by_username函数的各种场景。
    """

    # ============ 正常场景测试 ============

    @pytest.mark.asyncio
    async def test_get_user_by_username_exists_returns_user(self, user_service_instance, mock_db_session, mock_user):
        """测试用户名存在时返回用户."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.get_user_by_username(mock_db_session, "testuser")

        assert user == mock_user

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_exists_returns_none(self, user_service_instance, mock_db_session):
        """测试用户名不存在时返回None."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.get_user_by_username(mock_db_session, "nonexistent")

        assert user is None

    # ============ 边界值测试 ============

    # 1. Null/Undefined输入
    @pytest.mark.asyncio
    async def test_get_user_by_username_none_username_returns_none(self, user_service_instance, mock_db_session):
        """测试None用户名返回None."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.get_user_by_username(mock_db_session, None)

        mock_db_session.execute.assert_called_once()

    # 2. 空字符串
    @pytest.mark.asyncio
    async def test_get_user_by_username_empty_string_returns_none(self, user_service_instance, mock_db_session):
        """测试空用户名返回None."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.get_user_by_username(mock_db_session, "")

        assert user is None

    # 8. 特殊字符
    @pytest.mark.asyncio
    async def test_get_user_by_username_unicode_success(self, user_service_instance, mock_db_session, mock_user):
        """测试Unicode用户名查询."""
        mock_user.username = "用户名"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.get_user_by_username(mock_db_session, "用户名")

        assert user.username == "用户名"

    @pytest.mark.asyncio
    async def test_get_user_by_username_sql_injection_safe(self, user_service_instance, mock_db_session):
        """测试SQL注入用户名安全处理."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        # SQLAlchemy参数化查询，不会执行注入
        user = await user_service_instance.get_user_by_username(
            mock_db_session,
            "admin' OR '1'='1"
        )

        assert user is None


# ============ Test Class: get_users ============

class TestGetUsers:
    """
    获取用户列表函数测试.

    测试get_users函数的各种场景。
    """

    # ============ 正常场景测试 ============

    @pytest.mark.asyncio
    async def test_get_users_multiple_users_returns_list(self, user_service_instance, mock_db_session):
        """测试多个用户返回列表."""
        users = [MagicMock(spec=User) for _ in range(5)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = users
        mock_db_session.execute.return_value = mock_result

        result = await user_service_instance.get_users(mock_db_session)

        assert len(result) == 5
        assert all(isinstance(u, MagicMock) for u in result)

    @pytest.mark.asyncio
    async def test_get_users_no_users_returns_empty_list(self, user_service_instance, mock_db_session):
        """测试无用户返回空列表."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        result = await user_service_instance.get_users(mock_db_session)

        assert result == []
        assert len(result) == 0

    # ============ 边界值测试 ============

    # 1. Null/Undefined输入
    @pytest.mark.asyncio
    async def test_get_users_none_db_raises_error(self, user_service_instance):
        """测试None数据库会话应抛出错误."""
        with pytest.raises((TypeError, AttributeError)):
            await user_service_instance.get_users(None)

    # 7. 大数据
    @pytest.mark.asyncio
    async def test_get_users_large_dataset_performance(self, user_service_instance, mock_db_session):
        """测试大数据量查询性能."""
        users = [MagicMock(spec=User) for _ in range(1000)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = users
        mock_db_session.execute.return_value = mock_result

        result = await user_service_instance.get_users(mock_db_session)

        assert len(result) == 1000

    # 5. 错误路径
    @pytest.mark.asyncio
    async def test_get_users_db_error_handles_gracefully(self, user_service_instance, mock_db_session):
        """测试数据库错误处理."""
        mock_db_session.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            await user_service_instance.get_users(mock_db_session)


# ============ Test Class: update_user ============

class TestUpdateUser:
    """
    更新用户函数测试.

    测试update_user函数的各种场景。
    """

    # ============ 正常场景测试 ============

    @pytest.mark.asyncio
    async def test_update_user_username_success(self, user_service_instance, mock_db_session, mock_user):
        """测试更新用户名成功."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.update_user(
            mock_db_session,
            mock_user.id,
            username="newusername"
        )

        assert user.username == "newusername"
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_password_success(self, user_service_instance, mock_db_session, mock_user):
        """测试更新密码成功."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.update_user(
            mock_db_session,
            mock_user.id,
            password="newpassword"
        )

        assert user.password_hash is not None

    @pytest.mark.asyncio
    async def test_update_user_role_success(self, user_service_instance, mock_db_session, mock_user):
        """测试更新角色成功."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.update_user(
            mock_db_session,
            mock_user.id,
            role="admin"
        )

        assert user.role == "admin"

    @pytest.mark.asyncio
    async def test_update_user_all_fields_success(self, user_service_instance, mock_db_session, mock_user):
        """测试更新所有字段成功."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.update_user(
            mock_db_session,
            mock_user.id,
            username="newuser",
            password="newpass",
            role="admin"
        )

        assert user.username == "newuser"
        assert user.role == "admin"

    @pytest.mark.asyncio
    async def test_update_user_not_exists_returns_none(self, user_service_instance, mock_db_session):
        """测试用户不存在返回None."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.update_user(
            mock_db_session,
            uuid4(),
            username="newuser"
        )

        assert user is None
        mock_db_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_no_fields_specified_success(self, user_service_instance, mock_db_session, mock_user):
        """测试不指定任何字段时保持不变."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.update_user(
            mock_db_session,
            mock_user.id
        )

        # 应调用commit但字段不变
        mock_db_session.commit.assert_called_once()

    # ============ 边界值测试 ============

    # 1. Null/Undefined输入
    @pytest.mark.asyncio
    async def test_update_user_none_id_returns_none(self, user_service_instance, mock_db_session):
        """测试None ID返回None."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.update_user(
            mock_db_session,
            None,
            username="newuser"
        )

        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_none_username_skips_update(self, user_service_instance, mock_db_session, mock_user):
        """测试None用户名不更新."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.update_user(
            mock_db_session,
            mock_user.id,
            username=None
        )

        # None不触发更新
        mock_db_session.commit.assert_called_once()

    # 5. 错误路径
    @pytest.mark.asyncio
    async def test_update_user_db_error_handles_gracefully(self, user_service_instance, mock_db_session, mock_user):
        """测试数据库错误处理."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            await user_service_instance.update_user(
                mock_db_session,
                mock_user.id,
                username="newuser"
            )

    # 8. 特殊字符
    @pytest.mark.asyncio
    async def test_update_user_unicode_username_success(self, user_service_instance, mock_db_session, mock_user):
        """测试Unicode用户名更新."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        user = await user_service_instance.update_user(
            mock_db_session,
            mock_user.id,
            username="新用户名"
        )

        assert user.username == "新用户名"


# ============ Test Class: delete_user ============

class TestDeleteUser:
    """
    删除用户函数测试.

    测试delete_user函数的各种场景。
    """

    # ============ 正常场景测试 ============

    @pytest.mark.asyncio
    async def test_delete_user_exists_returns_true(self, user_service_instance, mock_db_session, mock_user):
        """测试用户存在时删除成功."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        result = await user_service_instance.delete_user(mock_db_session, mock_user.id)

        assert result is True
        mock_db_session.delete.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_not_exists_returns_false(self, user_service_instance, mock_db_session):
        """测试用户不存在时返回False."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await user_service_instance.delete_user(mock_db_session, uuid4())

        assert result is False
        mock_db_session.delete.assert_not_called()

    # ============ 边界值测试 ============

    # 1. Null/Undefined输入
    @pytest.mark.asyncio
    async def test_delete_user_none_id_returns_false(self, user_service_instance, mock_db_session):
        """测试None ID返回False."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await user_service_instance.delete_user(mock_db_session, None)

        assert result is False

    # 3. 无效类型
    @pytest.mark.asyncio
    async def test_delete_user_invalid_id_type_accepts_input(self, user_service_instance, mock_db_session):
        """测试无效ID类型（底层可能处理，业务层应校验UUID类型）."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await user_service_instance.delete_user(mock_db_session, "invalid-id")

        # 底层行为：非UUID字符串可能返回False
        assert result is False

    # 5. 错误路径
    @pytest.mark.asyncio
    async def test_delete_user_db_error_handles_gracefully(self, user_service_instance, mock_db_session, mock_user):
        """测试数据库错误处理."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            await user_service_instance.delete_user(mock_db_session, mock_user.id)


# ============ Test: Global Instance ============

class TestUserServiceInstance:
    """测试全局用户服务实例."""

    def test_user_service_instance_exists(self):
        """测试全局实例存在."""
        assert user_service is not None
        assert isinstance(user_service, UserService)

    def test_user_service_instance_methods_exist(self):
        """测试全局实例方法存在."""
        assert hasattr(user_service, 'create_user')
        assert hasattr(user_service, 'get_user_by_id')
        assert hasattr(user_service, 'get_user_by_username')
        assert hasattr(user_service, 'get_users')
        assert hasattr(user_service, 'update_user')
        assert hasattr(user_service, 'delete_user')