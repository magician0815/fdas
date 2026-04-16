"""
Session服务.

提供Session CRUD操作.

Author: FDAS Team
Created: 2026-04-03
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.session import Session


class SessionService:
    """Session服务类."""

    async def create_session(
        self,
        db: AsyncSession,
        user_id: UUID,
        expires_hours: int = 24,
        session_data: dict = None,
        ip_address: str = None,
    ) -> Session:
        """
        创建Session.

        Args:
            db: 数据库会话
            user_id: 用户ID
            expires_hours: 过期时间（小时）
            session_data: Session数据
            ip_address: 创建时的IP地址（可选，用于安全验证）

        Returns:
            Session: 创建的Session对象
        """
        if session_data is None:
            session_data = {}

        session = Session(
            user_id=user_id,
            session_data=session_data,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_hours),
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    async def get_session_by_id(
        self,
        db: AsyncSession,
        session_id: UUID,
    ) -> Optional[Session]:
        """
        根据ID获取Session.

        Args:
            db: 数据库会话
            session_id: Session ID

        Returns:
            Optional[Session]: Session对象
        """
        result = await db.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_sessions_by_user_id(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> list[Session]:
        """
        根据用户ID获取所有Session.

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            list[Session]: Session列表
        """
        result = await db.execute(
            select(Session).where(Session.user_id == user_id)
        )
        return result.scalars().all()

    async def delete_session(
        self,
        db: AsyncSession,
        session_id: UUID,
    ) -> bool:
        """
        删除Session.

        Args:
            db: 数据库会话
            session_id: Session ID

        Returns:
            bool: 是否删除成功
        """
        session = await self.get_session_by_id(db, session_id)
        if not session:
            return False

        await db.delete(session)
        await db.commit()
        return True

    async def delete_sessions_by_user_id(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> int:
        """
        删除用户所有Session.

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            int: 删除的Session数量
        """
        result = await db.execute(
            delete(Session).where(Session.user_id == user_id)
        )
        await db.commit()
        return result.rowcount

    async def cleanup_expired_sessions(
        self,
        db: AsyncSession,
    ) -> int:
        """
        清理过期Session.

        Args:
            db: 数据库会话

        Returns:
            int: 删除的Session数量
        """
        result = await db.execute(
            delete(Session).where(Session.expires_at < datetime.now(timezone.utc))
        )
        await db.commit()
        return result.rowcount


# 全局Session服务实例
session_service = SessionService()