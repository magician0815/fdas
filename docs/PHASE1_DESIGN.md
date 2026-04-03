# FDAS 第一阶段详细设计文档

> 金融数据抓取与分析系统 - 第一阶段实现设计说明书

**版本**: 1.0
**创建日期**: 2026-04-03
**作者**: FDAS Team

---

## 一、第一阶段概述

### 1.1 开发目标

第一阶段聚焦技术框架搭建和核心功能实现，完成USDCNH汇率数据的自动采集与可视化展示。

**核心目标**：
1. 完成技术框架搭建（配置、日志、数据库）
2. 完成用户认证与权限管理
3. 完成USDCNH数据采集与入库
4. 完成K线/均线/MACD可视化展示
5. 完成数据源和采集任务的Web配置

### 1.2 模块清单（22项）

| # | 模块 | 类型 | 优先级 | 状态 |
|---|------|------|--------|------|
| 1 | 项目目录结构 | 基础 | P0 | ✅ 已完成 |
| 2 | Claude记忆系统框架 | 基础 | P0 | ✅ 已完成 |
| 3 | PRD文档 | 文档 | P0 | ✅ 已完成 |
| 4 | ARCHITECTURE文档 | 文档 | P0 | ✅ 已完成 |
| 5 | CODE_STANDARDS文档 | 文档 | P0 | ✅ 已完成 |
| 6 | PERMISSION_DESIGN文档 | 文档 | P0 | ✅ 已完成 |
| 7 | PHASE1_DESIGN文档 | 文档 | P0 | 🔄 进行中 |
| 8 | 数据库初始化 | 后端 | P0 | 待开发 |
| 9 | 配置管理模块 | 后端 | P0 | 待开发 |
| 10 | 日志管理模块 | 后端 | P0 | 待开发 |
| 11 | 用户管理模块 | 后端 | P1 | 待开发 |
| 12 | 权限管理模块 | 后端 | P1 | 待开发 |
| 13 | 数据采集模块 | 后端 | P1 | 待开发 |
| 14 | 技术指标模块 | 后端 | P1 | 待开发 |
| 15 | 前端框架+菜单 | 前端 | P0 | 待开发 |
| 16 | 前端登录页面 | 前端 | P1 | 待开发 |
| 17 | 数据可视化页面 | 前端 | P1 | 待开发 |
| 18 | 数据源管理页面 | 前端 | P2 | 待开发 |
| 19 | 采集任务管理页面 | 前端 | P2 | 待开发 |
| 20 | 用户管理页面 | 前端 | P2 | 待开发 |
| 21 | 系统日志页面 | 前端 | P2 | 待开发 |
| 22 | 集成测试 | 测试 | P0 | 待开发 |

### 1.3 开发顺序

```
阶段一：文档（已完成）
├── PRD ✅
├── ARCHITECTURE ✅
├── CODE_STANDARDS ✅
├── PERMISSION_DESIGN ✅
└── PHASE1_DESIGN 🔄

阶段二：后端基础
├── 数据库初始化
├── 配置管理模块
└── 日志管理模块

阶段三：后端业务
├── 用户管理模块
├── 权限管理模块
├── 数据采集模块
└── 技术指标模块

阶段四：前端基础
└── 前端框架+菜单

阶段五：前端页面
├── 登录页面
├── 数据可视化页面
├── 数据源管理页面
├── 采集任务管理页面
├── 用户管理页面
└── 系统日志页面

阶段六：测试
└── 集成测试
```

---

## 二、数据库初始化模块

### 2.1 模块概述

| 属性 | 说明 |
|------|------|
| **模块名称** | 数据库初始化 |
| **优先级** | P0 |
| **依赖** | 无 |
| **产出** | PostgreSQL表结构、Alembic迁移脚本 |

### 2.2 实现思路

#### 2.2.1 数据库连接

```python
# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    获取数据库会话.

    用于FastAPI依赖注入.

    Yields:
        AsyncSession: 数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

#### 2.2.2 SQLAlchemy模型定义

**用户模型**：

```python
# backend/app/models/user.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class User(Base):
    """
    用户模型.

    Attributes:
        id: 用户ID（UUID）
        username: 用户名（唯一）
        password_hash: 密码hash
        role: 角色（admin/user）
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Session模型**：

```python
# backend/app/models/session.py
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.core.database import Base


class Session(Base):
    """
    Session模型.

    Attributes:
        id: Session ID（UUID）
        user_id: 用户ID（外键）
        session_data: Session数据（JSON）
        created_at: 创建时间
        expires_at: 过期时间
    """
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False)
```

**汇率数据模型**：

```python
# backend/app/models/fx_data.py
from sqlalchemy import Column, String, Date, Numeric, BigInteger, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, date
import uuid

from app.core.database import Base


class FXData(Base):
    """
    汇率数据模型.

    Attributes:
        id: 数据ID（UUID）
        symbol: 汇率符号（如USDCNH）
        date: 日期
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量
        created_at: 创建时间
    """
    __tablename__ = "fx_data"
    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uq_fx_data_symbol_date"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Numeric(10, 4))
    high = Column(Numeric(10, 4))
    low = Column(Numeric(10, 4))
    close = Column(Numeric(10, 4))
    volume = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
```

#### 2.2.3 Alembic迁移配置

```ini
# backend/alembic.ini
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = postgresql+asyncpg://fdas:fdas@localhost:5432/fdas

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic
```

```python
# backend/alembic/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context

from app.core.database import Base
from app.models import user, session, fx_data, datasource, collection_task

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline():
    """离线模式运行迁移."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """执行迁移."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """在线模式运行异步迁移."""
    connectable = create_async_engine(config.get_main_option("sqlalchemy.url"))
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def run_migrations_online():
    """在线模式运行迁移."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**初始迁移脚本**：

```python
# backend/alembic/versions/001_initial.py
"""初始表结构

Revision ID: 001
Create Date: 2026-04-03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 创建uuid扩展
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # users表
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_users_username', 'users', ['username'], unique=True)

    # sessions表
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_data', postgresql.JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('idx_sessions_expires_at', 'sessions', ['expires_at'])

    # fx_data表
    op.create_table(
        'fx_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('open', sa.Numeric(10, 4)),
        sa.Column('high', sa.Numeric(10, 4)),
        sa.Column('low', sa.Numeric(10, 4)),
        sa.Column('close', sa.Numeric(10, 4)),
        sa.Column('volume', sa.BigInteger),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('symbol', 'date', name='uq_fx_data_symbol_date'),
    )
    op.create_index('idx_fx_data_symbol', 'fx_data', ['symbol'])
    op.create_index('idx_fx_data_date', 'fx_data', ['date'])

    # datasources表
    op.create_table(
        'datasources',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(50), nullable=False, server_default='akshare'),
        sa.Column('config', postgresql.JSONB, nullable=False),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # collection_tasks表
    op.create_table(
        'collection_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('datasource_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_data', sa.String(100), nullable=False),
        sa.Column('cron_expression', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('last_run_at', sa.DateTime(timezone=True)),
        sa.Column('next_run_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_collection_tasks_datasource_id', 'collection_tasks', ['datasource_id'])

    # apscheduler_jobs表
    op.create_table(
        'apscheduler_jobs',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('next_run_time', sa.DateTime(timezone=True)),
        sa.Column('job_state', sa.LargeBinary, nullable=False),
    )
    op.create_index('idx_apscheduler_jobs_next_run_time', 'apscheduler_jobs', ['next_run_time'])


def downgrade():
    op.drop_table('apscheduler_jobs')
    op.drop_table('collection_tasks')
    op.drop_table('datasources')
    op.drop_table('fx_data')
    op.drop_table('sessions')
    op.drop_table('users')
```

### 2.3 验收标准

| 验收项 | 验收方式 | 通过标准 |
|--------|---------|---------|
| 数据库连接 | `alembic upgrade head` | 无错误输出 |
| 表结构创建 | `\dt` in psql | 6张表存在 |
| 索引创建 | `\di` in psql | 索引存在 |
| 默认admin用户 | `SELECT * FROM users` | admin用户存在 |

---

## 三、配置管理模块

### 3.1 模块概述

| 属性 | 说明 |
|------|------|
| **模块名称** | 配置管理模块 |
| **优先级** | P0 |
| **依赖** | 数据库初始化 |
| **产出** | Pydantic Settings配置类 |

### 3.2 实现思路

配置管理已在项目骨架中创建（`backend/app/config/settings.py`），需确认功能正确。

**验证脚本**：

```python
# backend/tests/test_config.py
from app.config.settings import settings


def test_settings_load():
    """测试配置加载."""
    assert settings.LOG_LEVEL is not None
    assert settings.DEFAULT_MA_PERIOD == 20
    assert settings.FX_DATA_LIMIT == 1000


def test_settings_types():
    """测试配置类型."""
    assert isinstance(settings.DEBUG, bool)
    assert isinstance(settings.APP_PORT, int)
    assert isinstance(settings.ALLOWED_ORIGINS, list)
```

### 3.3 验收标准

| 验收项 | 验收方式 | 通过标准 |
|--------|---------|---------|
| 配置加载 | `pytest tests/test_config.py` | 测试通过 |
| 环境变量覆盖 | 设置`DEBUG=true`运行 | 配置值被覆盖 |
| 类型转换 | 读取`APP_PORT` | 自动转为int |

---

## 四、日志管理模块

### 4.1 模块概述

| 属性 | 说明 |
|------|------|
| **模块名称** | 日志管理模块 |
| **优先级** | P0 |
| **依赖** | 配置管理模块 |
| **产出** | 日志配置函数、日志器获取函数 |

### 4.2 实现思路

日志管理已在项目骨架中创建（`backend/app/config/logging.py`），需确认功能正确。

**验证脚本**：

```python
# backend/tests/test_logging.py
import logging
from app.config.logging import setup_logging, get_logger


def test_setup_logging():
    """测试日志配置."""
    setup_logging()
    logger = get_logger("test")
    assert logger.level == logging.INFO


def test_logger_output(caplog):
    """测试日志输出."""
    logger = get_logger("test")
    with caplog.at_level(logging.INFO):
        logger.info("测试日志")
    assert "测试日志" in caplog.text
```

### 4.3 验收标准

| 验收项 | 验收方式 | 通过标准 |
|--------|---------|---------|
| 日志配置 | `pytest tests/test_logging.py` | 测试通过 |
| 控制台输出 | 运行应用 | 日志输出到控制台 |
| 文件输出 | 检查`logs/app.log` | 日志文件存在 |
| 文件轮转 | 写入大量日志 | 轮转文件生成 |

---

## 五、用户管理模块

### 5.1 模块概述

| 属性 | 说明 |
|------|------|
| **模块名称** | 用户管理模块 |
| **优先级** | P1 |
| **依赖** | 日志管理模块 |
| **产出** | 用户API、Session认证、登录/登出功能 |

### 5.2 实现思路

#### 5.2.1 密码服务

```python
# backend/app/services/auth_service.py
import bcrypt
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User


def hash_password(password: str) -> str:
    """
    密码加密.

    使用bcrypt算法加密密码.

    Args:
        password: 明文密码

    Returns:
        str: 加密后的密码hash
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    密码验证.

    Args:
        password: 明文密码
        password_hash: 密码hash

    Returns:
        bool: 密码是否正确
    """
    return bcrypt.checkpw(
        password.encode('utf-8'),
        password_hash.encode('utf-8')
    )


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    用户认证.

    Args:
        db: 数据库会话
        username: 用户名
        password: 密码

    Returns:
        Optional[User]: 认证成功返回用户对象，失败返回None
    """
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None

    return user
```

#### 5.2.2 用户服务

```python
# backend/app/services/user_service.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.services.auth_service import hash_password


async def create_user(
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


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
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


async def get_users(db: AsyncSession) -> List[User]:
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
    user = await get_user_by_id(db, user_id)
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


async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
    """
    删除用户.

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        bool: 是否删除成功
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return False

    await db.delete(user)
    await db.commit()
    return True
```

#### 5.2.3 用户API

```python
# backend/app/api/v1/users.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import Response, PaginatedResponse
from app.services import user_service

router = APIRouter()


@router.get("/", response_model=Response)
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    获取用户列表.

    仅admin可访问.
    """
    users = await user_service.get_users(db)
    return Response(
        success=True,
        data=[UserResponse.model_validate(u) for u in users],
    )


@router.post("/", response_model=Response)
async def create_user(
    request: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    创建用户.

    仅admin可访问.
    """
    user = await user_service.create_user(
        db=db,
        username=request.username,
        password=request.password,
        role=request.role,
    )
    return Response(
        success=True,
        data=UserResponse.model_validate(user),
        message="用户创建成功",
    )


@router.put("/{user_id}", response_model=Response)
async def update_user(
    user_id: str,
    request: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    更新用户.

    仅admin可访问.
    """
    user = await user_service.update_user(
        db=db,
        user_id=user_id,
        **request.model_dump(exclude_unset=True),
    )
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return Response(
        success=True,
        data=UserResponse.model_validate(user),
        message="用户更新成功",
    )


@router.delete("/{user_id}", response_model=Response)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    删除用户.

    仅admin可访问.
    """
    success = await user_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return Response(success=True, message="用户删除成功")
```

### 5.3 验收标准

| 验收项 | 验收方式 | 通过标准 |
|--------|---------|---------|
| 用户登录 | POST /api/v1/auth/login | 返回Session Cookie |
| 用户登出 | POST /api/v1/auth/logout | Cookie被清除 |
| 用户列表 | GET /api/v1/users (admin) | 返回用户列表 |
| 创建用户 | POST /api/v1/users (admin) | 用户创建成功 |
| 更新用户 | PUT /api/v1/users/{id} (admin) | 用户更新成功 |
| 删除用户 | DELETE /api/v1/users/{id} (admin) | 用户删除成功 |
| 权限检查 | user访问用户API | 返回403 |

---

## 六、权限管理模块

### 6.1 模块概述

| 属性 | 说明 |
|------|------|
| **模块名称** | 权限管理模块 |
| **优先级** | P1 |
| **依赖** | 用户管理模块 |
| **产出** | 权限依赖注入、路由守卫 |

### 6.2 实现思路

权限管理已在PERMISSION_DESIGN文档中详细设计，核心实现：

**后端权限依赖注入**：

```python
# backend/app/core/deps.py
from fastapi import Depends, HTTPException
from app.core.security import get_current_user
from app.models.user import User


async def require_login(
    current_user: User = Depends(get_current_user),
) -> User:
    """要求登录."""
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """要求admin权限."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user
```

### 6.3 验收标准

| 验收项 | 验收方式 | 通过标准 |
|--------|---------|---------|
| admin访问 | admin用户访问用户API | 返回200 |
| user访问 | user用户访问用户API | 返回403 |
| 未登录访问 | 无Cookie访问受保护API | 返回401 |

---

## 七、数据采集模块

### 7.1 模块概述

| 属性 | 说明 |
|------|------|
| **模块名称** | 数据采集模块 |
| **优先级** | P1 |
| **依赖** | 权限管理模块 |
| **产出** | AKShare采集器、APScheduler调度、数据入库 |

### 7.2 实现思路

#### 7.2.1 AKShare采集器

```python
# backend/app/collectors/akshare_collector.py
import akshare as ak
import pandas as pd
from typing import List, Dict
from datetime import date, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.logging import get_logger

logger = get_logger(__name__)


class AKShareCollector:
    """
    AKShare数据采集器.

    使用AKShare库采集金融数据，支持重试机制.
    """

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def collect_usdcnh(
        self,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        采集USDCNH汇率数据.

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            List[Dict]: 汇率数据列表

        Raises:
            Exception: 采集失败
        """
        logger.info(f"开始采集USDCNH数据: {start_date} ~ {end_date}")

        try:
            # 调用AKShare接口
            df = ak.fx_spot_quote_usdcnh(
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
            )

            # 转换为字典列表
            records = df.to_dict('records')

            logger.info(f"成功采集{len(records)}条USDCNH数据")
            return self._transform_data(records)

        except Exception as e:
            logger.error(f"采集USDCNH数据失败: {str(e)}")
            raise

    def _transform_data(self, records: List[Dict]) -> List[Dict]:
        """
        转换数据格式.

        将AKShare返回的数据转换为数据库存储格式.

        Args:
            records: 原始数据

        Returns:
            List[Dict]: 转换后的数据
        """
        transformed = []
        for record in records:
            transformed.append({
                "symbol": "USDCNH",
                "date": record.get("date"),
                "open": record.get("open"),
                "high": record.get("high"),
                "low": record.get("low"),
                "close": record.get("close"),
                "volume": record.get("volume"),
            })
        return transformed
```

#### 7.2.2 数据采集服务

```python
# backend/app/services/fx_service.py
from typing import List
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.models.fx_data import FXData
from app.collectors.akshare_collector import AKShareCollector
from app.config.logging import get_logger

logger = get_logger(__name__)


class FXDataService:
    """
    汇率数据服务.

    负责数据采集、存储、查询等业务逻辑.
    """

    def __init__(self):
        self.collector = AKShareCollector()

    async def collect_and_save(
        self,
        db: AsyncSession,
        symbol: str = "USDCNH",
        days: int = 30,
    ) -> int:
        """
        采集并保存数据.

        Args:
            db: 数据库会话
            symbol: 汇率符号
            days: 采集天数

        Returns:
            int: 保存的数据条数
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # 采集数据
        records = await self.collector.collect_usdcnh(start_date, end_date)

        # 批量插入（使用ON CONFLICT处理重复）
        for record in records:
            stmt = insert(FXData).values(**record)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_fx_data_symbol_date",
                set_=dict(
                    open=stmt.excluded.open,
                    high=stmt.excluded.high,
                    low=stmt.excluded.low,
                    close=stmt.excluded.close,
                    volume=stmt.excluded.volume,
                )
            )
            await db.execute(stmt)

        await db.commit()
        logger.info(f"成功保存{len(records)}条{symbol}数据")
        return len(records)

    async def get_fx_data(
        self,
        db: AsyncSession,
        symbol: str = "USDCNH",
        start_date: date = None,
        end_date: date = None,
        limit: int = 1000,
    ) -> List[FXData]:
        """
        查询汇率数据.

        Args:
            db: 数据库会话
            symbol: 汇率符号
            start_date: 开始日期
            end_date: 结束日期
            limit: 数据条数限制

        Returns:
            List[FXData]: 汇率数据列表
        """
        query = select(FXData).where(FXData.symbol == symbol)

        if start_date:
            query = query.where(FXData.date >= start_date)
        if end_date:
            query = query.where(FXData.date <= end_date)

        query = query.order_by(FXData.date.desc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()
```

#### 7.2.3 APScheduler调度服务

```python
# backend/app/services/scheduler_service.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from typing import Callable

from app.config.settings import settings
from app.config.logging import get_logger

logger = get_logger(__name__)


class SchedulerService:
    """
    任务调度服务.

    管理APScheduler任务配置和执行.
    """

    def __init__(self):
        jobstores = {
            'default': SQLAlchemyJobStore(
                url=settings.DATABASE_URL.replace('+asyncpg', '')
            )
        }
        self.scheduler = AsyncIOScheduler(jobstores=jobstores)

    def start(self):
        """启动调度器."""
        self.scheduler.start()
        logger.info("APScheduler调度器已启动")

    def shutdown(self):
        """关闭调度器."""
        self.scheduler.shutdown()
        logger.info("APScheduler调度器已关闭")

    def add_job(
        self,
        job_id: str,
        func: Callable,
        cron_expression: str,
        **kwargs,
    ):
        """
        添加定时任务.

        Args:
            job_id: 任务ID
            func: 执行函数
            cron_expression: cron表达式（如 "0 18 * * *"）
        """
        # 解析cron表达式
        parts = cron_expression.split()
        trigger = CronTrigger(
            minute=parts[0],
            hour=parts[1],
            day=parts[2],
            month=parts[3],
            day_of_week=parts[4],
        )

        self.scheduler.add_job(
            id=job_id,
            func=func,
            trigger=trigger,
            **kwargs,
        )
        logger.info(f"添加任务: {job_id}, cron: {cron_expression}")

    def remove_job(self, job_id: str):
        """
        移除任务.

        Args:
            job_id: 任务ID
        """
        self.scheduler.remove_job(job_id)
        logger.info(f"移除任务: {job_id}")

    def pause_job(self, job_id: str):
        """暂停任务."""
        self.scheduler.pause_job(job_id)
        logger.info(f"暂停任务: {job_id}")

    def resume_job(self, job_id: str):
        """恢复任务."""
        self.scheduler.resume_job(job_id)
        logger.info(f"恢复任务: {job_id}")

    def get_jobs(self):
        """获取所有任务."""
        return self.scheduler.get_jobs()


# 全局调度器实例
scheduler_service = SchedulerService()
```

### 7.3 验收标准

| 验收项 | 验收方式 | 通过标准 |
|--------|---------|---------|
| 数据采集 | 手动触发采集 | 数据入库成功 |
| 任务调度 | 添加定时任务 | 任务按时执行 |
| 数据查询 | GET /api/v1/fx/data | 返回汇率数据 |
| 数据去重 | 重复采集同一天数据 | 数据不重复 |

---

## 八、技术指标模块

### 8.1 模块概述

| 属性 | 说明 |
|------|------|
| **模块名称** | 技术指标模块 |
| **优先级** | P1 |
| **依赖** | 数据采集模块 |
| **产出** | MA/MACD计算服务 |

### 8.2 实现思路

```python
# backend/app/services/technical_service.py
import talib
import numpy as np
from typing import List, Dict
from decimal import Decimal

from app.models.fx_data import FXData
from app.config.settings import settings


class TechnicalService:
    """
    技术指标计算服务.

    使用TA-Lib计算MA、MACD等技术指标.
    """

    def calculate_ma(
        self,
        data: List[FXData],
        period: int = None,
    ) -> List[float]:
        """
        计算MA均线.

        Args:
            data: 汇率数据列表
            period: 周期（默认使用配置）

        Returns:
            List[float]: MA值列表
        """
        if period is None:
            period = settings.DEFAULT_MA_PERIOD

        # 提取收盘价
        close_prices = np.array([
            float(d.close) for d in reversed(data)
        ])

        # 计算MA
        ma = talib.MA(close_prices, timeperiod=period)

        # 转换为列表（过滤NaN）
        result = []
        for i, value in enumerate(ma):
            if not np.isnan(value):
                result.append({
                    "index": i,
                    "value": round(float(value), 4),
                })

        return result

    def calculate_macd(
        self,
        data: List[FXData],
        fast: int = None,
        slow: int = None,
        signal: int = None,
    ) -> Dict:
        """
        计算MACD指标.

        Args:
            data: 汇率数据列表
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            Dict: MACD数据（macd, signal, hist）
        """
        if fast is None:
            fast = settings.DEFAULT_MACD_FAST
        if slow is None:
            slow = settings.DEFAULT_MACD_SLOW
        if signal is None:
            signal = settings.DEFAULT_MACD_SIGNAL

        # 提取收盘价
        close_prices = np.array([
            float(d.close) for d in reversed(data)
        ])

        # 计算MACD
        macd, signal_line, hist = talib.MACD(
            close_prices,
            fastperiod=fast,
            slowperiod=slow,
            signalperiod=signal,
        )

        # 转换为列表
        result = {
            "macd": [],
            "signal": [],
            "hist": [],
        }

        for i in range(len(macd)):
            if not np.isnan(macd[i]):
                result["macd"].append(round(float(macd[i]), 4))
                result["signal"].append(round(float(signal_line[i]), 4))
                result["hist"].append(round(float(hist[i]), 4))

        return result

    def calculate_all_indicators(
        self,
        data: List[FXData],
    ) -> Dict:
        """
        计算所有技术指标.

        Args:
            data: 汇率数据列表

        Returns:
            Dict: 所有技术指标数据
        """
        return {
            "ma": self.calculate_ma(data),
            "macd": self.calculate_macd(data),
        }
```

### 8.3 验收标准

| 验收项 | 验收方式 | 通过标准 |
|--------|---------|---------|
| MA计算 | 调用calculate_ma | 返回MA值列表 |
| MACD计算 | 调用calculate_macd | 返回MACD数据 |
| API集成 | GET /api/v1/fx/indicators | 返回技术指标 |

---

## 九、前端框架模块

### 9.1 模块概述

| 属性 | 说明 |
|------|------|
| **模块名称** | 前端框架+菜单系统 |
| **优先级** | P0 |
| **依赖** | 无（可与后端并行开发） |
| **产出** | Vue项目框架、路由配置、侧边栏菜单 |

### 9.2 实现思路

前端框架已在项目骨架中创建，核心组件：

**布局组件**：

```vue
<!-- frontend/src/components/Layout.vue -->
<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="200px">
      <Sidebar />
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header>
        <Navbar />
      </el-header>

      <!-- 页面内容 -->
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
/**
 * 主布局组件.
 *
 * 包含侧边栏、顶部导航栏和主内容区.
 */
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
</script>

<style scoped>
.layout-container {
  height: 100vh;
}
</style>
```

**导航栏组件**：

```vue
<!-- frontend/src/components/Navbar.vue -->
<template>
  <div class="navbar">
    <div class="logo">FDAS</div>
    <div class="user-info">
      <el-dropdown>
        <span class="user-name">
          {{ authStore.user?.username }}
          <el-icon><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleLogout">登出</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const router = useRouter()

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>
```

### 9.3 验收标准

| 验收项 | 验收方式 | 通过标准 |
|--------|---------|---------|
| 页面访问 | npm run dev | 页面可访问 |
| 路由跳转 | 点击菜单 | 页面正确跳转 |
| 菜单显示 | 登录不同角色 | 菜单正确显示 |

---

## 十、前端页面模块

### 10.1 登录页面

```vue
<!-- frontend/src/views/Login.vue -->
<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>FDAS 登录</h2>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading">
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate()
  if (!valid) return

  loading.value = true
  const success = await authStore.login(form.username, form.password)
  loading.value = false

  if (success) {
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } else {
    ElMessage.error('用户名或密码错误')
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.login-card {
  width: 400px;
}
</style>
```

### 10.2 数据可视化页面

```vue
<!-- frontend/src/views/FXData.vue -->
<template>
  <div class="fx-data-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>USDCNH汇率走势</span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            @change="fetchData"
          />
        </div>
      </template>

      <FXChart :data="chartData" :indicators="indicators" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import FXChart from '@/components/FXChart.vue'
import { getFXData, getIndicators } from '@/api/fx_data'

const dateRange = ref([])
const chartData = ref([])
const indicators = ref({})

onMounted(async () => {
  await fetchData()
})

async function fetchData() {
  const response = await getFXData()
  chartData.value = response.data

  const indicatorsResponse = await getIndicators()
  indicators.value = indicatorsResponse.data
}
</script>
```

### 10.3 ECharts图表组件

```vue
<!-- frontend/src/components/FXChart.vue -->
<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: { type: Array, default: () => [] },
  indicators: { type: Object, default: () => ({}) },
})

const chartRef = ref()
let chartInstance = null

onMounted(() => {
  chartInstance = echarts.init(chartRef.value)
  updateChart()
})

watch(() => [props.data, props.indicators], updateChart, { deep: true })

function updateChart() {
  if (!props.data.length) return

  const option = {
    title: { text: 'USDCNH汇率走势' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['K线', 'MA20', 'MACD'] },
    grid: [
      { left: '10%', right: '8%', height: '50%' },
      { left: '10%', right: '8%', top: '65%', height: '20%' },
    ],
    xAxis: [
      { type: 'category', data: props.data.map(d => d.date), gridIndex: 0 },
      { type: 'category', data: props.data.map(d => d.date), gridIndex: 1 },
    ],
    yAxis: [
      { scale: true, gridIndex: 0 },
      { scale: true, gridIndex: 1 },
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: props.data.map(d => [d.open, d.close, d.low, d.high]),
      },
      {
        name: 'MA20',
        type: 'line',
        data: props.indicators.ma?.map(m => m.value) || [],
      },
      {
        name: 'MACD',
        type: 'line',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: props.indicators.macd?.macd || [],
      },
    ],
  }

  chartInstance.setOption(option)
}
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 500px;
}
</style>
```

### 10.4 Cron可视化配置组件

```vue
<!-- frontend/src/components/CronBuilder.vue -->
<template>
  <div class="cron-builder">
    <el-form :model="cronForm" label-width="100px">
      <el-form-item label="执行周期">
        <el-select v-model="cronForm.periodType" @change="updateCron">
          <el-option label="每天" value="daily" />
          <el-option label="每周" value="weekly" />
          <el-option label="每月" value="monthly" />
          <el-option label="自定义" value="custom" />
        </el-select>
      </el-form-item>

      <el-form-item label="执行时间">
        <el-time-picker v-model="cronForm.time" @change="updateCron" />
      </el-form-item>

      <el-form-item v-if="cronForm.periodType === 'weekly'" label="星期">
        <el-select v-model="cronForm.dayOfWeek" @change="updateCron">
          <el-option label="周一" value="1" />
          <el-option label="周二" value="2" />
          <el-option label="周三" value="3" />
          <el-option label="周四" value="4" />
          <el-option label="周五" value="5" />
          <el-option label="周六" value="6" />
          <el-option label="周日" value="0" />
        </el-select>
      </el-form-item>

      <el-form-item v-if="cronForm.periodType === 'monthly'" label="日期">
        <el-select v-model="cronForm.dayOfMonth" @change="updateCron">
          <el-option v-for="d in 31" :key="d" :label="`${d}日`" :value="String(d)" />
        </el-select>
      </el-form-item>

      <el-form-item label="Cron表达式">
        <el-input v-model="cronExpression" readonly />
        <span class="description">{{ cronDescription }}</span>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

const emit = defineEmits(['update:cron'])

const cronForm = reactive({
  periodType: 'daily',
  time: new Date(2024, 0, 1, 18, 0),
  dayOfWeek: '1',
  dayOfMonth: '1',
})

const cronExpression = computed(() => {
  const minute = cronForm.time.getMinutes()
  const hour = cronForm.time.getHours()

  switch (cronForm.periodType) {
    case 'daily':
      return `${minute} ${hour} * * *`
    case 'weekly':
      return `${minute} ${hour} * * ${cronForm.dayOfWeek}`
    case 'monthly':
      return `${minute} ${hour} ${cronForm.dayOfMonth} * *`
    default:
      return ''
  }
})

const cronDescription = computed(() => {
  const hour = cronForm.time.getHours()
  const minute = cronForm.time.getMinutes()
  const timeStr = `${hour}:${minute.toString().padStart(2, '0')}`

  switch (cronForm.periodType) {
    case 'daily':
      return `每天 ${timeStr} 执行`
    case 'weekly':
      return `每周${['日', '一', '二', '三', '四', '五', '六'][cronForm.dayOfWeek]} ${timeStr} 执行`
    case 'monthly':
      return `每月${cronForm.dayOfMonth}日 ${timeStr} 执行`
    default:
      return ''
  }
})

function updateCron() {
  emit('update:cron', cronExpression.value)
}
</script>
```

### 10.5 验收标准

| 页面 | 验收项 | 通过标准 |
|------|--------|---------|
| Login | 登录功能 | 登录成功跳转首页 |
| FXData | 图表展示 | K线/均线/MACD正确显示 |
| DataSource | CRUD操作 | 数据源配置成功 |
| Collection | 任务配置 | 可视化cron配置正确 |
| Users | 用户管理 | 用户CRUD成功 |
| Logs | 日志查看 | 日志列表正确显示 |

---

## 十一、集成测试

### 11.1 测试场景

| 场景 | 测试步骤 | 预期结果 |
|------|---------|---------|
| **完整流程测试** | 1. 启动Docker环境<br>2. 访问前端<br>3. admin登录<br>4. 查看数据分析<br>5. 配置数据源<br>6. 创建采集任务<br>7. 触发采集<br>8. 查看数据 | 所有操作成功 |
| **权限测试** | 1. user登录<br>2. 访问用户管理 | 返回403 |
| **数据测试** | 1. 采集数据<br>2. 查询数据<br>3. 查看图表 | 数据正确显示 |

### 11.2 验收标准

| 验收项 | 验收方式 | 通过标准 |
|--------|---------|---------|
| Docker启动 | docker-compose up -d | 所有容器正常运行 |
| 端到端测试 | 手动操作 | 所有功能可用 |
| 性能测试 | 查询1000条数据 | 响应<500ms |

---

## 十二、开发进度跟踪

### 12.1 进度文件更新

每完成一个模块后，更新以下文件：

1. **progress.md** - 更新当前状态、已完成模块、下一步任务
2. **module_signatures.md** - 添加模块签名
3. **MEMORY.md** - 更新已完成模块列表

### 12.2 中断恢复

开发中断后，按以下步骤恢复：

1. 读取 `MEMORY.md` 了解项目概况
2. 读取 `progress.md` 确认当前模块
3. 读取 `module_signatures.md` 了解已完成模块
4. 继续开发当前模块

---

## 十三、附录

### 13.1 相关文档

- [PRD.md](PRD.md) - 需求设计文档
- [ARCHITECTURE.md](ARCHITECTURE.md) - 技术架构文档
- [CODE_STANDARDS.md](CODE_STANDARDS.md) - 代码规范文档
- [PERMISSION_DESIGN.md](PERMISSION_DESIGN.md) - 权限设计文档

### 13.2 开发命令速查

```bash
# 后端开发
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# 前端开发
cd frontend
npm install
npm run dev

# Docker测试
cd docker
docker-compose up -d
docker-compose logs -f

# 测试
pytest backend/tests
npm run test --prefix frontend
```