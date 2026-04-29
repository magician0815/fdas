"""
认证API路由.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-16 - 实现logout Session清除、IP绑定、登录速率限制
Updated: 2026-04-16 - 支持测试环境禁用速率限制
"""

import os
from uuid import UUID
from functools import wraps
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.schemas.auth import LoginRequest, UserResponse
from app.schemas.common import Response
from app.services.auth_service import authenticate_user
from app.services.session_service import session_service

router = APIRouter()

# 检测是否在测试环境中
TESTING = os.environ.get("TESTING", "").lower() in ("true", "1", "yes")

# 速率限制器：登录接口限制每分钟5次尝试（测试环境禁用）
limiter = Limiter(key_func=get_remote_address, enabled=not TESTING)


# 可信代理IP列表（用于X-Forwarded-For验证）
# 仅当请求来自这些代理IP时，才信任X-Forwarded-For头
TRUSTED_PROXIES = ["127.0.0.1", "::1", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]


def _get_client_ip_safe(request: Request) -> str:
    """
    安全获取客户端IP地址.

    仅信任来自可信代理的X-Forwarded-For头，防止IP伪造攻击.

    Args:
        request: HTTP请求对象

    Returns:
        str: 客户端IP地址
    """
    # 获取直接连接IP（始终可信）
    direct_ip = request.client.host if request.client else None

    # 检查X-Forwarded-For头
    x_forwarded_for = request.headers.get("X-Forwarded-For")

    if x_forwarded_for:
        # 检查直接连接IP是否来自可信代理
        if direct_ip and _is_trusted_proxy(direct_ip):
            # 可信代理来的请求，信任X-Forwarded-For
            return x_forwarded_for.split(",")[0].strip()
        else:
            # 不可信来源，忽略X-Forwarded-For，使用直接IP
            return direct_ip or "unknown"

    return direct_ip or "unknown"


def _is_trusted_proxy(ip: str) -> bool:
    """
    检查IP是否来自可信代理.

    Args:
        ip: IP地址

    Returns:
        bool: 是否可信代理
    """
    import ipaddress

    try:
        # 检查是否匹配已知可信代理IP
        for trusted in TRUSTED_PROXIES:
            if "/" in trusted:
                # CIDR格式（如 10.0.0.0/8）
                if ipaddress.ip_address(ip) in ipaddress.ip_network(trusted):
                    return True
            elif ip == trusted:
                return True
    except Exception:
        pass
    return False


def rate_limit(limit_string: str):
    """
    条件速率限制装饰器.

    测试环境返回空装饰器，生产环境使用slowapi限制.
    """
    if TESTING:
        # 测试环境：返回空装饰器
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    else:
        # 生产环境：使用slowapi
        return limiter.limit(limit_string)


@router.post("/login", response_model=Response)
@rate_limit("5/minute")
async def login(
    request_body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    用户登录.

    Args:
        request_body: 登录请求
        request: HTTP请求对象（用于获取IP和速率限制）
        db: 数据库会话

    Returns:
        Response: 登录结果
    """
    # 验证用户
    user = await authenticate_user(db, request_body.username, request_body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 获取客户端IP地址（安全版本，防止IP伪造）
    client_ip = _get_client_ip_safe(request)

    # 创建Session（带IP绑定）
    session = await session_service.create_session(
        db=db,
        user_id=user.id,
        expires_hours=24,
        ip_address=client_ip,
    )

    return Response(
        success=True,
        data={
            "user": UserResponse(
                id=str(user.id),
                username=user.username,
                role=user.role,
            ),
            "session_id": str(session.id),
        },
        message="登录成功",
    )


@router.post("/logout", response_model=Response)
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    用户登出.

    从请求头获取session_id并清除对应Session记录.

    Args:
        request: 请求对象
        db: 数据库会话

    Returns:
        Response: 登出结果
    """
    # 从请求头获取session_id
    session_id = request.headers.get("X-Session-ID")

    if session_id:
        try:
            # 删除Session记录
            await session_service.delete_session(db, UUID(session_id))
        except ValueError:
            # session_id格式无效，忽略
            pass

    return Response(
        success=True,
        message="登出成功",
    )


@router.get("/me", response_model=Response)
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前登录用户信息.

    从请求头获取session_id，验证Session有效性并返回用户信息.

    Args:
        request: 请求对象
        db: 数据库会话

    Returns:
        Response: 用户信息
    """
    # 从请求头获取session_id
    session_id = request.headers.get("X-Session-ID")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
        )

    try:
        # 验证Session并获取用户信息
        session = await session_service.get_session_by_id(db, UUID(session_id))
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session已过期",
            )

        # 获取用户信息
        from app.services.user_service import user_service
        user = await user_service.get_user_by_id(db, session.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
            )

        return Response(
            success=True,
            data={
                "user": UserResponse(
                    id=str(user.id),
                    username=user.username,
                    role=user.role,
                ),
            },
            message=None,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session格式无效",
        )