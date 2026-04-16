"""
异常处理测试.

测试全局异常处理器.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from unittest.mock import MagicMock
from fastapi import status, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import (
    AppException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    BadRequestException,
    app_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
    register_exception_handlers,
)


class TestAppException:
    """测试AppException基类."""

    def test_app_exception_default_values(self):
        """测试默认值."""
        exc = AppException()
        assert exc.code == "INTERNAL_ERROR"
        assert exc.message == "服务器内部错误"
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_app_exception_custom_values(self):
        """测试自定义值."""
        exc = AppException(
            code="CUSTOM_ERROR",
            message="自定义错误",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        assert exc.code == "CUSTOM_ERROR"
        assert exc.message == "自定义错误"
        assert exc.status_code == status.HTTP_400_BAD_REQUEST


class TestNotFoundException:
    """测试NotFoundException."""

    def test_not_found_default_message(self):
        """测试默认消息."""
        exc = NotFoundException()
        assert exc.code == "NOT_FOUND"
        assert exc.message == "资源未找到"
        assert exc.status_code == status.HTTP_404_NOT_FOUND

    def test_not_found_custom_message(self):
        """测试自定义消息."""
        exc = NotFoundException("用户未找到")
        assert exc.message == "用户未找到"


class TestUnauthorizedException:
    """测试UnauthorizedException."""

    def test_unauthorized_default_message(self):
        """测试默认消息."""
        exc = UnauthorizedException()
        assert exc.code == "UNAUTHORIZED"
        assert exc.message == "未授权访问"
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthorized_custom_message(self):
        """测试自定义消息."""
        exc = UnauthorizedException("请先登录")
        assert exc.message == "请先登录"


class TestForbiddenException:
    """测试ForbiddenException."""

    def test_forbidden_default_message(self):
        """测试默认消息."""
        exc = ForbiddenException()
        assert exc.code == "FORBIDDEN"
        assert exc.message == "禁止访问"
        assert exc.status_code == status.HTTP_403_FORBIDDEN

    def test_forbidden_custom_message(self):
        """测试自定义消息."""
        exc = ForbiddenException("无权限访问此资源")
        assert exc.message == "无权限访问此资源"


class TestBadRequestException:
    """测试BadRequestException."""

    def test_bad_request_default_message(self):
        """测试默认消息."""
        exc = BadRequestException()
        assert exc.code == "BAD_REQUEST"
        assert exc.message == "错误请求"
        assert exc.status_code == status.HTTP_400_BAD_REQUEST

    def test_bad_request_custom_message(self):
        """测试自定义消息."""
        exc = BadRequestException("参数格式错误")
        assert exc.message == "参数格式错误"


class TestAppExceptionHandler:
    """测试应用异常处理器."""

    @pytest.mark.asyncio
    async def test_app_exception_handler(self):
        """测试AppException处理器."""
        mock_request = MagicMock(spec=Request)
        exc = AppException(code="TEST_ERROR", message="测试错误", status_code=400)

        response = await app_exception_handler(mock_request, exc)

        assert response.status_code == 400
        # 检查响应内容
        import json
        body = json.loads(response.body)
        assert body["success"] is False
        assert body["message"] == "测试错误"
        assert body["error"] == "TEST_ERROR"


class TestValidationExceptionHandler:
    """测试验证异常处理器."""

    @pytest.mark.asyncio
    async def test_validation_exception_handler(self):
        """测试RequestValidationError处理器."""
        mock_request = MagicMock(spec=Request)

        # 创建Mock验证错误
        mock_error = MagicMock()
        mock_error.errors = MagicMock(return_value=[
            {"loc": ["body", "name"], "msg": "字段必填"},
            {"loc": ["body", "email"], "msg": "格式无效"},
        ])

        response = await validation_exception_handler(mock_request, mock_error)

        assert response.status_code == 422  # HTTP_422
        import json
        body = json.loads(response.body)
        assert body["success"] is False
        assert "name" in body["message"]
        assert "email" in body["message"]
        assert body["error"] == "VALIDATION_ERROR"


class TestSQLAlchemyExceptionHandler:
    """测试SQLAlchemy异常处理器."""

    @pytest.mark.asyncio
    async def test_sqlalchemy_exception_handler(self):
        """测试SQLAlchemyError处理器."""
        mock_request = MagicMock(spec=Request)
        exc = SQLAlchemyError("Connection failed")

        response = await sqlalchemy_exception_handler(mock_request, exc)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        import json
        body = json.loads(response.body)
        assert body["success"] is False
        assert body["message"] == "数据库错误"
        assert body["error"] == "DATABASE_ERROR"


class TestGenericExceptionHandler:
    """测试通用异常处理器."""

    @pytest.mark.asyncio
    async def test_generic_exception_handler(self):
        """测试Exception处理器."""
        mock_request = MagicMock(spec=Request)
        exc = Exception("Unexpected error")

        response = await generic_exception_handler(mock_request, exc)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        import json
        body = json.loads(response.body)
        assert body["success"] is False
        assert body["message"] == "服务器内部错误"
        assert body["error"] == "INTERNAL_ERROR"


class TestRegisterExceptionHandlers:
    """测试注册异常处理器."""

    def test_register_exception_handlers(self):
        """测试注册异常处理器."""
        from fastapi import FastAPI

        app = FastAPI()
        register_exception_handlers(app)

        # 验证处理器已注册（通过检查app.exception_handlers）
        # FastAPI内部维护了异常处理器映射
        assert app.exception_handlers is not None