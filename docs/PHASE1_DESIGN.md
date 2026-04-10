# FDAS 第一阶段详细设计文档

> 金融数据抓取与分析系统 - 第一阶段实现设计说明书

**版本**: 1.3
**创建日期**: 2026-04-03
**更新日期**: 2026-04-10
**作者**: FDAS Team

---

## 一、第一阶段概述

### 1.1 开发目标

第一阶段聚焦技术框架搭建和核心功能实现，完成外汇汇率数据的自动采集与可视化展示。

**核心目标（必须验收）**：
1. 完成技术框架搭建（配置、日志、数据库）
2. 完成用户认证与权限管理
3. **完成外汇数据实际采集与入库（使用AKShare forex_hist接口，非模拟数据）**
4. **完成K线/均线/MACD可视化展示（基于真实数据）**
5. **完成数据源和采集任务的Web配置（功能可用，支持参数校验）**

### 1.2 核心验收标准

| 核心功能 | 验收标准 | 验收方式 |
|----------|----------|----------|
| 数据采集 | 调用AKShare真实采集USDCNH数据入库 | 数据库有真实数据 |
| 定时调度 | APScheduler启动并按cron执行采集 | 任务按时触发 |
| 数据展示 | K线/MA/MACD图表基于真实数据渲染 | 图表正确显示 |
| 数据源配置 | Web端修改配置后生效 | 配置保存成功 |
| 采集任务配置 | Web端创建/启停任务生效 | 任务状态变更 |

### 1.3 模块清单（22项）

| # | 模块 | 类型 | 优先级 | 当前状态 |
|---|------|------|--------|----------|
| 1 | 项目目录结构 | 基础 | P0 | ✅ 已完成 |
| 2 | Claude记忆系统框架 | 基础 | P0 | ✅ 已完成 |
| 3 | PRD文档 | 文档 | P0 | ✅ 已完成 |
| 4 | ARCHITECTURE文档 | 文档 | P0 | ✅ 已完成 |
| 5 | CODE_STANDARDS文档 | 文档 | P0 | ✅ 已完成 |
| 6 | PERMISSION_DESIGN文档 | 文档 | P0 | ✅ 已完成 |
| 7 | PHASE1_DESIGN文档 | 文档 | P0 | ✅ 已完成 |
| 8 | 数据库初始化 | 后端 | P0 | ✅ 已完成 |
| 9 | 配置管理模块 | 后端 | P0 | ✅ 已完成 |
| 10 | 日志管理模块 | 后端 | P0 | ✅ 已完成 |
| 11 | 用户管理模块 | 后端 | P1 | ✅ 已完成 |
| 12 | 权限管理模块 | 后端 | P1 | ✅ 已完成 |
| 13 | 数据采集模块 | 后端 | P0 | ❌ **待完成** |
| 14 | 技术指标模块 | 后端 | P1 | ⚠️ 部分完成 |
| 15 | 前端框架+菜单 | 前端 | P0 | ✅ 已完成 |
| 16 | 前端登录页面 | 前端 | P1 | ✅ 已完成 |
| 17 | 数据可视化页面 | 前端 | P0 | ❌ **待完成** |
| 18 | 数据源管理页面 | 前端 | P0 | ❌ **待完成** |
| 19 | 采集任务管理页面 | 前端 | P0 | ❌ **待完成** |
| 20 | 用户管理页面 | 前端 | P1 | ⚠️ 骨架完成 |
| 21 | 系统日志页面 | 前端 | P1 | ⚠️ 骨架完成 |
| 22 | 集成测试 | 测试 | P0 | ⚠️ 部分完成 |

### 1.4 开发顺序

```
阶段一：文档（已完成）✅
├── PRD ✅
├── ARCHITECTURE ✅
├── CODE_STANDARDS ✅
├── PERMISSION_DESIGN ✅
└── PHASE1_DESIGN ✅

阶段二：后端基础（已完成）✅
├── 数据库初始化 ✅
├── 配置管理模块 ✅
└── 日志管理模块 ✅

阶段三：后端业务（部分完成）
├── 用户管理模块 ✅
├── 权限管理模块 ✅
├── 数据采集模块 ❌ 待完成
└── 技术指标模块 ⚠️ 部分完成

阶段四：前端基础（已完成）✅
└── 前端框架+菜单 ✅

阶段五：前端页面（部分完成）
├── 登录页面 ✅
├── 数据可视化页面 ❌ 待完成（核心）
├── 数据源管理页面 ❌ 待完成（核心）
├── 采集任务管理页面 ❌ 待完成（核心）
├── 用户管理页面 ⚠️ 骨架完成
└── 系统日志页面 ⚠️ 骨架完成

阶段六：测试
└── 集成测试 ⚠️ 待完善
```

---

## 二、数据库初始化模块

### 2.1 模块概述

| 属性 | 说明 |
|------|------|
| **模块名称** | 数据库初始化 |
| **优先级** | P0 |
| **依赖** | 无 |
| **产出** | PostgreSQL表结构、init-db.sql初始化脚本 |

### 2.2 实现思路

> **重要变更**：项目开发过程中不使用Alembic迁移脚本，而是维护一份完整的数据库初始化脚本（`docker/init-db.sql`）。每次表结构更新直接修改此脚本，部署时清空数据库后执行一遍即可完成所有模型部署。这样简化了开发阶段的数据库迭代流程。

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
from sqlalchemy import Column, String, Date, Numeric, BigInteger, DateTime, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class FXData(Base):
    """
    汇率数据模型.

    Attributes:
        id: 数据ID（UUID）
        symbol: 货币对名称（中文，如"美元人民币"）
        symbol_code: 货币对代码（英文，如"USDCNY"）
        date: 交易日期
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量（外汇通常为0）
        change_pct: 涨跌幅(%)
        change_amount: 涨跌额
        amplitude: 振幅(%)
        created_at: 创建时间
    """
    __tablename__ = "fx_data"
    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uq_fx_data_symbol_date"),
        Index("idx_fx_data_symbol_code", "symbol_code"),
        Index("idx_fx_data_symbol_date", "symbol", "date"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="数据唯一标识ID")
    symbol = Column(String(50), nullable=False, index=True, comment="货币对名称（中文）")
    symbol_code = Column(String(20), nullable=False, comment="货币对代码（英文）")
    date = Column(Date, nullable=False, index=True, comment="交易日期")
    open = Column(Numeric(10, 4), comment="开盘价")
    high = Column(Numeric(10, 4), comment="最高价")
    low = Column(Numeric(10, 4), comment="最低价")
    close = Column(Numeric(10, 4), comment="收盘价")
    volume = Column(BigInteger, default=0, comment="成交量（外汇数据为0）")
    change_pct = Column(Numeric(10, 4), comment="涨跌幅（百分比）")
    change_amount = Column(Numeric(10, 4), comment="涨跌额")
    amplitude = Column(Numeric(10, 4), comment="振幅（百分比）")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, comment="记录创建时间")
```

**数据源模型**：

```python
# backend/app/models/datasource.py
class DataSource(Base):
    """
    数据源模型.

    Attributes:
        id: 数据源ID（UUID）
        name: 数据源名称（唯一）
        interface: AKShare接口名称（如forex_hist）
        description: 数据源描述
        config_schema: 配置参数Schema（JSON，用于前端动态渲染表单）
        supported_symbols: 支持的货币对列表（JSON）
        min_date: 接口最早可用数据日期
        type: 数据源类型（默认akshare）
        is_active: 是否启用
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "datasources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="数据源唯一标识ID")
    name = Column(String(100), nullable=False, unique=True, comment="数据源名称")
    interface = Column(String(50), nullable=False, comment="AKShare接口名称")
    description = Column(Text, comment="数据源描述说明")
    config_schema = Column(JSONB, nullable=False, comment="配置参数Schema（前端表单渲染）")
    supported_symbols = Column(JSONB, comment="支持的货币对列表")
    min_date = Column(Date, comment="接口最早可用数据日期")
    type = Column(String(50), nullable=False, default="akshare", comment="数据源类型")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
```

**采集任务模型**：

```python
# backend/app/models/collection_task.py
class CollectionTask(Base):
    """
    采集任务模型.

    Attributes:
        id: 任务ID（UUID）
        name: 任务名称
        datasource_id: 数据源ID（外键）
        symbol: 货币对名称（中文）
        start_date: 采集开始日期
        end_date: 采集结束日期
        cron_expr: Cron表达式
        is_enabled: 是否启用
        last_run_at: 上次执行时间
        next_run_at: 下次执行时间
        last_status: 上次执行状态
        last_message: 上次执行消息
        last_records_count: 上次采集记录数
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "collection_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="任务唯一标识ID")
    name = Column(String(100), nullable=False, comment="任务名称")
    datasource_id = Column(UUID(as_uuid=True), ForeignKey("datasources.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联数据源ID")
    symbol = Column(String(50), nullable=False, comment="货币对名称（中文）")
    start_date = Column(Date, comment="采集开始日期")
    end_date = Column(Date, comment="采集结束日期")
    cron_expr = Column(String(100), comment="Cron定时表达式")
    is_enabled = Column(Boolean, default=False, comment="是否启用")
    last_run_at = Column(DateTime(timezone=True), comment="上次执行时间")
    next_run_at = Column(DateTime(timezone=True), comment="下次执行时间")
    last_status = Column(String(20), comment="上次执行状态")
    last_message = Column(Text, comment="上次执行消息")
    last_records_count = Column(Integer, default=0, comment="上次采集记录数")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
```

**采集任务日志模型**：

```python
# backend/app/models/collection_task_log.py
class CollectionTaskLog(Base):
    """
    采集任务执行日志模型.

    记录采集任务的每次执行情况.

    Attributes:
        id: 日志ID（UUID）
        task_id: 任务ID（外键）
        run_at: 执行时间
        status: 执行状态（success/failed/running）
        records_count: 采集记录数
        message: 执行消息/错误信息
        duration_ms: 执行耗时（毫秒）
        created_at: 创建时间
    """
    __tablename__ = "collection_task_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="日志唯一标识ID")
    task_id = Column(UUID(as_uuid=True), ForeignKey("collection_tasks.id", ondelete="CASCADE"), nullable=False, comment="关联任务ID")
    run_at = Column(DateTime(timezone=True), nullable=False, comment="执行时间")
    status = Column(String(20), nullable=False, comment="执行状态")
    records_count = Column(Integer, default=0, comment="采集记录数")
    message = Column(Text, comment="执行消息或错误信息")
    duration_ms = Column(Integer, comment="执行耗时（毫秒）")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, comment="创建时间")
```

#### 2.2.2 数据库初始化脚本

使用单份完整的初始化脚本替代Alembic迁移：

```sql
-- docker/init-db.sql
-- 完整的数据库初始化脚本
-- 每次表结构更新直接修改此脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 所有表定义（含字段注释）
CREATE TABLE IF NOT EXISTS users (...);
CREATE TABLE IF NOT EXISTS sessions (...);
CREATE TABLE IF NOT EXISTS datasources (...);
CREATE TABLE IF NOT EXISTS collection_tasks (...);
CREATE TABLE IF NOT EXISTS collection_task_logs (...);
CREATE TABLE IF NOT EXISTS fx_data (...);
CREATE TABLE IF NOT EXISTS apscheduler_jobs (...);

-- 所有字段中文注释
COMMENT ON COLUMN users.id IS '用户唯一标识ID';
COMMENT ON COLUMN users.username IS '用户名';
...

-- 所有索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
...

-- 初始数据
INSERT INTO users (...) VALUES (...) ON CONFLICT DO NOTHING;
INSERT INTO datasources (...) VALUES (...) ON CONFLICT DO NOTHING;
```

### 2.3 验收标准

| 验收项 | 验收方式 | 通过标准 |
|--------|---------|---------|
| 数据库连接 | `psql -h localhost -U fdas -d fdas` | 连接成功 |
| 表结构创建 | `\dt` in psql | 7张表存在（users, sessions, datasources, collection_tasks, collection_task_logs, fx_data, apscheduler_jobs） |
| 字段注释 | `\d+ users` in psql | 每个字段都有中文注释 |
| 索引创建 | `\di` in psql | 所有索引存在 |
| 默认admin用户 | `SELECT * FROM users` | admin用户存在 |
| 默认数据源 | `SELECT * FROM datasources` | forex_hist数据源存在 |

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
| **优先级** | P0 |
| **依赖** | 权限管理模块 |
| **产出** | AKShare采集器、APScheduler调度、数据入库、数据源管理API、采集任务管理API |

### 7.2 AKShare接口规范

#### 7.2.1 forex_hist接口

**接口名称**：`forex_hist` - 外汇日线行情

**输入参数**：

| 参数名 | 类型 | 必须 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `symbol` | str | Y | "美元人民币" | 货币对名称（中文） |
| `start_date` | str | N | "20200101" | 开始日期，格式：YYYYMMDD |
| `end_date` | str | N | "20241231" | 结束日期，格式：YYYYMMDD |
| `adjust` | str | N | "" | 复权类型（暂不支持） |

**返回字段**：

| 字段名 | 类型 | 描述 |
|--------|------|------|
| 日期 | datetime | 交易日期 |
| 开盘价 | float | 开盘价格 |
| 收盘价 | float | 收盘价格 |
| 最高价 | float | 最高价格 |
| 最低价 | float | 最低价格 |
| 成交量 | float | 成交量（外汇通常为0） |
| 涨跌幅 | float | 涨跌幅(%) |
| 涨跌额 | float | 涨跌额 |
| 振幅 | float | 振幅(%) |

**支持的货币对**：
```
美元人民币(USDCNY)、欧元美元(EURUSD)、英镑美元(GBPUSD)、美元日元(USDJPY)、
澳元美元(AUDUSD)、美元加元(USDCAD)、美元瑞郎(USDCHF)、新西兰元美元(NZDUSD)、
欧元英镑(EURGBP)、欧元日元(EURJPY)、英镑日元(GBPJPY)、澳元日元(AUDJPY)
```

### 7.3 实现思路

#### 7.3.1 AKShare采集器

```python
# backend/app/collectors/akshare_collector.py
"""
AKShare数据采集器.

使用AKShare库采集金融数据.
"""

import akshare as ak
import pandas as pd
from typing import List, Dict, Optional
from datetime import date
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


# 货币对名称与代码映射
SYMBOL_CODE_MAP = {
    "美元人民币": "USDCNY",
    "欧元美元": "EURUSD",
    "英镑美元": "GBPUSD",
    "美元日元": "USDJPY",
    "澳元美元": "AUDUSD",
    "美元加元": "USDCAD",
    "美元瑞郎": "USDCHF",
    "新西兰元美元": "NZDUSD",
    "欧元英镑": "EURGBP",
    "欧元日元": "EURJPY",
    "英镑日元": "GBPJPY",
    "澳元日元": "AUDJPY",
}


class AKShareCollector:
    """
    AKShare数据采集器.

    使用AKShare库采集外汇数据，支持重试机制.
    """

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def collect_forex_hist(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> List[Dict]:
        """
        采集外汇日线行情数据.

        Args:
            symbol: 货币对名称（中文，如"美元人民币"）
            start_date: 开始日期，格式YYYYMMDD
            end_date: 结束日期，格式YYYYMMDD

        Returns:
            List[Dict]: 汇率数据列表

        Raises:
            Exception: 采集失败
        """
        logger.info(f"开始采集外汇数据: {symbol}, {start_date} ~ {end_date}")

        try:
            # 调用AKShare forex_hist接口
            df = ak.forex_hist(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )

            if df.empty:
                logger.warning(f"采集数据为空: {symbol}")
                return []

            # 获取货币对英文代码
            symbol_code = SYMBOL_CODE_MAP.get(symbol, symbol)

            # 转换数据格式
            records = self._transform_data(df, symbol, symbol_code)

            logger.info(f"成功采集{len(records)}条{symbol}数据")
            return records

        except Exception as e:
            logger.error(f"采集外汇数据失败: {str(e)}")
            raise

    def _transform_data(
        self,
        df: pd.DataFrame,
        symbol: str,
        symbol_code: str,
    ) -> List[Dict]:
        """
        转换数据格式.

        将AKShare返回的DataFrame转换为数据库存储格式.

        Args:
            df: 原始DataFrame
            symbol: 货币对名称（中文）
            symbol_code: 货币对代码（英文）

        Returns:
            List[Dict]: 转换后的数据列表
        """
        records = []
        for _, row in df.iterrows():
            record = {
                "symbol": symbol,
                "symbol_code": symbol_code,
                "date": row.get("日期"),
                "open": row.get("开盘价"),
                "high": row.get("最高价"),
                "low": row.get("最低价"),
                "close": row.get("收盘价"),
                "volume": row.get("成交量", 0) or 0,
                "change_pct": row.get("涨跌幅"),
                "change_amount": row.get("涨跌额"),
                "amplitude": row.get("振幅"),
            }
            records.append(record)

        return records

    async def fetch_supported_symbols(self) -> List[Dict]:
        """
        获取支持的货币对列表.

        通过调用forex_spot_quote接口获取实时行情，从中解析货币对列表.

        Returns:
            List[Dict]: 货币对列表，格式：[{"value": "美元人民币", "code": "USDCNY"}]
        """
        try:
            # 获取人民币相关货币对
            df_rmb = ak.forex_spot_quote(symbol="人民币")

            # 解析货币对列表
            symbols = []
            seen = set()

            for _, row in df_rmb.iterrows():
                pair = row.get("货币对", "")
                # 解析货币对名称（需要转换为中文名称）
                symbol_name = self._parse_symbol_name(pair)
                symbol_code = self._parse_symbol_code(pair)

                if symbol_name and symbol_code and symbol_name not in seen:
                    seen.add(symbol_name)
                    symbols.append({
                        "value": symbol_name,
                        "code": symbol_code,
                        "label": f"{symbol_name} ({symbol_code})",
                    })

            return symbols

        except Exception as e:
            logger.error(f"获取货币对列表失败: {str(e)}")
            return []

    def _parse_symbol_name(self, pair: str) -> Optional[str]:
        """解析货币对中文名称."""
        # 实现货币对名称解析逻辑
        # 例如："人民币美元" -> 美元人民币（需反向）
        pass

    def _parse_symbol_code(self, pair: str) -> Optional[str]:
        """解析货币对英文代码."""
        # 实现代码解析逻辑
        pass
```

#### 7.3.2 数据采集服务

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

#### 7.3.3 APScheduler调度服务

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

### 7.4 验收标准

| 验收项 | 验收方式 | 通过标准 |
|--------|---------|---------|
| 数据采集 | 手动触发采集任务 | forex_hist接口调用成功，数据入库 |
| 任务调度 | 添加定时任务并启用 | APScheduler按时触发采集 |
| 数据查询 | GET /api/v1/fx/data | 返回汇率数据（OHLC格式） |
| 数据去重 | 重复采集同一天数据 | 数据不重复（ON CONFLICT更新） |
| 货币对选择 | 选择不同货币对采集 | 不同货币对数据正确入库 |
| 数据源配置 | Web端查看/编辑数据源 | 配置Schema正确展示 |
| 采集任务配置 | Web端创建/启停任务 | 任务状态变更生效 |
| 自动获取货币对 | 点击自动获取按钮 | 返回最新货币对列表并显示变更 |

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