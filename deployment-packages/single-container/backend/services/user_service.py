"""
用户服务.

提供用户CRUD操作.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-16 - 添加类型转换和安全性验证
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
            username: 用户名（会转换为字符串）
            password: 密码（会转换为字符串）
            role: 角色

        Returns:
            User: 创建的用户对象

        Note:
            类型转换在底层完成，业务验证应在API/Schema层执行.
        """
        # 类型转换：支持各种输入类型
        if username is not None and not isinstance(username, str):
            username = str(username)
        if password is not None and not isinstance(password, str):
            password = str(password)

        # 安全性检查：None值会导致bcrypt错误，需提前处理
        if password is None:
            raise ValueError("密码不能为None")

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

    async def get_users(
        self,
        db: AsyncSession,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[User]:
        """
        获取用户列表.

        Args:
            db: 数据库会话
            limit: 返回数量限制（None表示不限制）
            offset: 偏移量（用于分页）

        Returns:
            List[User]: 用户列表
        """
        query = select(User).offset(offset)
        if limit is not None:
            query = query.limit(limit)
        result = await db.execute(query)
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