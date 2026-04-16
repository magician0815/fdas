"""
权限依赖注入.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-16 - WebSocket添加origin验证，Session添加IP验证
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.session import Session
from app.config.settings import settings

logger = logging.getLogger(__name__)

# 允许的WebSocket连接origin列表（从配置读取）
ALLOWED_WS_ORIGINS = getattr(settings, 'ALLOWED_ORIGINS', ['http://localhost:5173', 'http://localhost:3000'])

# 是否启用Session IP验证（可通过环境变量配置）
ENABLE_IP_VALIDATION = getattr(settings, 'ENABLE_IP_VALIDATION', False)


def _get_client_ip(request: Request) -> Optional[str]:
    """
    获取客户端IP地址.

    优先使用X-Forwarded-For（代理场景），否则使用直接连接IP.

    Args:
        request: HTTP请求对象

    Returns:
        Optional[str]: 客户端IP地址
    """
    client_ip = request.headers.get("X-Forwarded-For")
    if client_ip:
        # X-Forwarded-For可能包含多个IP，取第一个
        client_ip = client_ip.split(",")[0].strip()
    elif request.client:
        client_ip = request.client.host
    return client_ip


async def get_current_user_ws(
    websocket: WebSocket,
    db: AsyncSession,
) -> Optional[str]:
    """
    WebSocket连接的用户认证.

    从WebSocket query参数或headers获取session_id并验证.
    同时验证origin防止跨站WebSocket劫持.

    Args:
        websocket: WebSocket连接对象
        db: 数据库会话

    Returns:
        Optional[str]: 用户ID（验证成功）或None（验证失败）
    """
    # Origin验证：防止跨站WebSocket劫持
    origin = websocket.headers.get("origin") or websocket.headers.get("Origin")
    if origin:
        # 检查origin是否在允许列表中
        origin_allowed = False
        for allowed in ALLOWED_WS_ORIGINS:
            # 支持精确匹配和通配符（如 *.example.com）
            if origin == allowed or origin.startswith(allowed.rstrip('*')):
                origin_allowed = True
                break
        if not origin_allowed:
            logger.warning(f"WebSocket连接被拒绝：不允许的origin={origin}")
            return None

    # 从query参数获取session_id
    session_id = websocket.query_params.get("session_id")

    # 如果query参数没有，尝试从headers获取
    if not session_id:
        session_id = websocket.headers.get("X-Session-ID")

    if not session_id:
        return None

    # 验证session有效性（过期时间检查）
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.expires_at > datetime.now(timezone.utc)
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        return None

    return str(session.user_id)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    获取当前登录用户.

    通过请求头或Cookie中的session_id验证用户身份.
    可选启用IP验证防止Session劫持.

    Raises:
        HTTPException: 401未授权
    """
    # 从请求头获取session_id
    session_id = request.headers.get("X-Session-ID")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
        )

    # 验证session有效性（过期时间检查）
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.expires_at > datetime.now(timezone.utc)
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="会话已过期或无效",
        )

    # IP验证（可选安全增强）
    if ENABLE_IP_VALIDATION and session.ip_address:
        current_ip = _get_client_ip(request)
        if current_ip and current_ip != session.ip_address:
            logger.warning(
                f"Session IP不匹配: session_id={session_id}, "
                f"创建IP={session.ip_address}, 当前IP={current_ip}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="会话IP验证失败，请重新登录",
            )

    # 获取用户
    result = await db.execute(
        select(User).where(User.id == session.user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    return user


async def require_login(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    要求用户已登录.

    Args:
        current_user: 当前用户

    Returns:
        User: 已登录用户
    """
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    要求admin权限.

    Args:
        current_user: 当前用户

    Returns:
        User: admin用户

    Raises:
        HTTPException: 403权限不足
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user