"""
全局异常处理.

提供统一的异常处理和错误响应格式.

Author: FDAS Team
Created: 2026-04-03
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """
    应用异常基类.

    Attributes:
        code: 错误代码
        message: 错误消息
        status_code: HTTP状态码
    """

    def __init__(
        self,
        code: str = "INTERNAL_ERROR",
        message: str = "服务器内部错误",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code


class NotFoundException(AppException):
    """资源未找到异常."""

    def __init__(self, message: str = "资源未找到"):
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UnauthorizedException(AppException):
    """未授权异常."""

    def __init__(self, message: str = "未授权访问"):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(AppException):
    """禁止访问异常."""

    def __init__(self, message: str = "禁止访问"):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class BadRequestException(AppException):
    """错误请求异常."""

    def __init__(self, message: str = "错误请求"):
        super().__init__(
            code="BAD_REQUEST",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    应用异常处理器.

    Args:
        request: 请求对象
        exc: 应用异常

    Returns:
        JSONResponse: 统一错误响应
    """
    logger.warning(f"AppException: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "message": exc.message,
            "error": exc.code,
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    请求验证异常处理器.

    Args:
        request: 请求对象
        exc: 验证异常

    Returns:
        JSONResponse: 统一错误响应
    """
    errors = exc.errors()
    error_messages = [f"{e.get('loc', [])[-1]}: {e.get('msg', '')}" for e in errors]
    message = "; ".join(error_messages)

    logger.warning(f"ValidationError: {message}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "data": None,
            "message": message,
            "error": "VALIDATION_ERROR",
        },
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """
    SQLAlchemy异常处理器.

    Args:
        request: 请求对象
        exc: SQLAlchemy异常

    Returns:
        JSONResponse: 统一错误响应
    """
    logger.error(f"SQLAlchemyError: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "data": None,
            "message": "数据库错误",
            "error": "DATABASE_ERROR",
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    通用异常处理器.

    Args:
        request: 请求对象
        exc: 异常

    Returns:
        JSONResponse: 统一错误响应
    """
    logger.error(f"Unhandled Exception: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "data": None,
            "message": "服务器内部错误",
            "error": "INTERNAL_ERROR",
        },
    )


def register_exception_handlers(app):
    """
    注册异常处理器到FastAPI应用.

    Args:
        app: FastAPI应用实例
    """
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)