"""
用户服务.

提供用户CRUD操作.

Author: FDAS Team
Created: 2026-04-03
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.services.auth_service import hash_password


class UserService:
    """用户服务类."""

    async def create_user(
        self,
        db: AsyncSession,
        username: str,
        password: str,
        role: str = "user",
    ) -> User:
        """
        创建用户.

        Args:
            db: 数据库会话
            username: 用户名
            password: 密码
            role: 角色

        Returns:
            User: 创建的用户对象
        """
        user = User(
            username=username,
            password_hash=hash_password(password),
            role=role,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def get_user_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """
        根据ID获取用户.

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            Optional[User]: 用户对象
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """
        根据用户名获取用户.

        Args:
            db: 数据库会话
            username: 用户名

        Returns:
            Optional[User]: 用户对象
        """
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_users(self, db: AsyncSession) -> List[User]:
        """
        获取用户列表.

        Args:
            db: 数据库会话

        Returns:
            List[User]: 用户列表
        """
        result = await db.execute(select(User))
        return result.scalars().all()

    async def update_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        username: Optional[str] = None,
        password: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Optional[User]:
        """
        更新用户.

        Args:
            db: 数据库会话
            user_id: 用户ID
            username: 新用户名
            password: 新密码
            role: 新角色

        Returns:
            Optional[User]: 更新后的用户对象
        """
        user = await self.get_user_by_id(db, user_id)
        if not user:
            return None

        if username:
            user.username = username
        if password:
            user.password_hash = hash_password(password)
        if role:
            user.role = role

        await db.commit()
        await db.refresh(user)
        return user

    async def delete_user(self, db: AsyncSession, user_id: UUID) -> bool:
        """
        删除用户.

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            bool: 是否删除成功
        """
        user = await self.get_user_by_id(db, user_id)
        if not user:
            return False

        await db.delete(user)
        await db.commit()
        return True


# 全局用户服务实例
user_service = UserService()