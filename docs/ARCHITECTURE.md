# FDAS 技术架构文档

> 金融数据抓取与分析系统 - 技术架构说明书

**版本**: 1.1
**创建日期**: 2026-04-03
**更新日期**: 2026-04-10
**作者**: FDAS Team

---

## 一、架构概述

### 1.1 设计原则

| 原则 | 说明 | 实现方式 |
|------|------|---------|
| **分层解耦** | 六层独立，接口清晰 | 层间通过API/消息通信 |
| **全开源** | 无商业软件依赖 | FastAPI/Vue3/PostgreSQL/AKShare |
| **异步优先** | 提升并发性能 | FastAPI async + SQLAlchemy async |
| **容器化** | 简化部署运维 | Docker Compose编排 |
| **可扩展** | 预留扩展接口 | 插件式模块设计 |

### 1.2 六层架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     第七层：预留扩展层                            │
│  (通用数据源、数据备份、Token监控、性能监控等)                     │
│                          ↕ 双向连接                              │
├─────────────────────────────────────────────────────────────────┤
│                     第六层：集成对接层                            │
│                     (飞书 Webhook 告警推送)                       │
│                          ↕ API调用                               │
├─────────────────────────────────────────────────────────────────┤
│                     第五层：前端展示层                            │
│  Vue 3 + Element Plus + ECharts + Pinia + Vite                  │
│                          ↕ RESTful API                           │
├─────────────────────────────────────────────────────────────────┤
│                     第四层：后端服务层                            │
│  FastAPI + SQLAlchemy 2.0 + Pydantic + APScheduler              │
│                          ↕ Async ORM                             │
├─────────────────────────────────────────────────────────────────┤
│                     第三层：数据存储层                            │
│                     PostgreSQL 16                                │
│                          ↕ SQL/连接池                            │
├─────────────────────────────────────────────────────────────────┤
│                     第二层：数据采集层                            │
│  Python + AKShare + APScheduler + tenacity + TA-Lib             │
│                          ↕ HTTP请求                               │
├─────────────────────────────────────────────────────────────────┤
│                     第一层：基础设施层                            │
│               Docker Desktop + Ubuntu 22.04                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、技术栈选型

### 2.1 技术栈清单

| 层级 | 技术 | 版本 | 选型理由 |
|------|------|------|---------|
| **基础设施** | Docker Desktop | 最新 | 容器化开发测试环境 |
| | Ubuntu 22.04 | LTS | 稳定的Linux基础镜像 |
| **数据采集** | Python | 3.11 | 性能优化，类型提示完善 |
| | AKShare | 1.12+ | 开源金融数据接口，覆盖全面 |
| | APScheduler | 3.10+ | 灵活的任务调度，支持PostgreSQL持久化 |
| | tenacity | 8.2+ | 简洁的重试机制 |
| | TA-Lib | 0.4.28 | 业界标准技术指标库 |
| | pandas | 2.0+ | 数据处理，配合TA-Lib |
| **数据存储** | PostgreSQL | 16 | 最新稳定版，性能优化 |
| | asyncpg | 0.29+ | 高性能异步PostgreSQL驱动 |
| **后端服务** | FastAPI | 0.110+ | 高性能异步API框架 |
| | SQLAlchemy | 2.0+ | 异步ORM，类型提示完善 |
| | Pydantic | 2.5+ | 数据验证，Settings管理 |
| | Uvicorn | 0.27+ | ASGI服务器 |
| | cachetools | 5.3+ | 内存缓存，TTL/LRU策略 |
| **前端展示** | Vue | 3.4+ | Composition API，性能优化 |
| | Element Plus | 2.5+ | Vue3组件库，UI统一 |
| | ECharts | 5.5+ | 金融图表，功能完善 |
| | Pinia | 2.1+ | Vue3状态管理 |
| | Axios | 1.6+ | HTTP客户端 |
| | Vite | 5.0+ | 快速构建工具 |
| **测试** | pytest | 7.4+ | Python测试框架 |
| | pytest-asyncio | 0.23+ | 异步测试支持 |
| | Vitest | 1.2+ | Vue测试框架 |
| | Vue Test Utils | 2.4+ | Vue组件测试 |

### 2.2 技术栈依赖关系

```
前端构建 (Vite)
    ↓
Vue 3 应用
    ↓
Element Plus + ECharts + Pinia + Axios
    ↓
HTTP请求 (RESTful API)
    ↓
FastAPI (Uvicorn)
    ↓
SQLAlchemy 2.0 (asyncpg) + Pydantic + APScheduler
    ↓
PostgreSQL 16
    ↓
数据采集 (AKShare + TA-Lib)
    ↓
外部数据源
```

---

## 三、容器架构设计

### 3.1 容器编排方案

**选择：前后端合并容器**

| 方案 | 优点 | 缺点 | 选择理由 |
|------|------|------|---------|
| 前后端合并 | 部署简单，资源占用少 | 扩展性受限 | 第一阶段足够，简化运维 |
| 前后端分离 | 独立扩展，灵活部署 | 多容器管理复杂 | 第二阶段可切换 |
| Nginx代理 | 架构清晰，性能优化 | 多一层代理 | 生产环境推荐 |

### 3.2 容器架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Desktop                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  fdas-app                            │   │
│  │  ┌─────────────────────────────────────────────────┐│   │
│  │  │  Nginx (可选，第一阶段不启用)                    ││   │
│  │  └─────────────────────────────────────────────────┘│   │
│  │  ┌─────────────────┐  ┌───────────────────────────┐ │   │
│  │  │  FastAPI        │  │  Vue 3 Static Files       │ │   │
│  │  │  (Uvicorn)      │  │  (Vite构建产物)           │ │   │
│  │  │  Port: 8000     │  │  /static/*                │ │   │
│  │  │  /api/*         │  │  index.html               │ │   │
│  │  └─────────────────┘  └───────────────────────────┘ │   │
│  │                                                      │   │
│  │  Dockerfile: backend/Dockerfile                      │   │
│  │  前端构建: frontend/Dockerfile (多阶段构建)          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  fdas-db                             │   │
│  │  ┌─────────────────────────────────────────────────┐│   │
│  │  │  PostgreSQL 16                                  ││   │
│  │  │  Port: 5432                                     ││   │
│  │  │  User: fdas                                     ││   │
│  │  │  Database: fdas                                 ││   │
│  │  │  Volume: fdas-db-data                           ││   │
│  │  └─────────────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Docker Compose配置

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  fdas-db:
    image: postgres:16
    container_name: fdas-db
    environment:
      POSTGRES_USER: fdas
      POSTGRES_PASSWORD: fdas
      POSTGRES_DB: fdas
    ports:
      - "5432:5432"
    volumes:
      - fdas-db-data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fdas"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  fdas-app:
    build:
      context: ../backend
      dockerfile: Dockerfile
    container_name: fdas-app
    environment:
      DATABASE_URL: postgresql+asyncpg://fdas:fdas@fdas-db:5432/fdas
      SESSION_SECRET: ${SESSION_SECRET:-change-this-in-production}
      DEBUG: ${DEBUG:-false}
    ports:
      - "8000:8000"
    depends_on:
      fdas-db:
        condition: service_healthy
    volumes:
      - ../backend/logs:/app/logs
    restart: unless-stopped

volumes:
  fdas-db-data:
    driver: local
```

### 3.4 部署流程

```
1. 构建前端
   cd frontend && npm run build
   → 产出: frontend/dist/

2. 复制前端构建产物到后端
   cp -r frontend/dist backend/static

3. 构建后端镜像（包含前端静态文件）
   docker build -t fdas-app backend/

4. 启动容器
   cd docker && docker-compose up -d

5. 访问服务
   http://localhost:8000 (前端页面)
   http://localhost:8000/api/docs (API文档)
```

---

## 四、数据库设计

### 4.1 设计理念

| 设计原则 | 说明 |
|---------|------|
| 市场独立管理 | 每个市场独立建立标的基础信息表，采集时明确指定存入市场 |
| 行情按市场分表 | 不同市场行情数据存储在不同表中，便于字段差异化和管理 |
| 时间分区优化 | 大表使用PostgreSQL原生分区，按时间范围分片 |
| 数据来源追踪 | 行情表记录datasource_id，支持同一标的多数据源 |
| 更新时间追踪 | 行情表记录updated_at，知道数据何时被更新 |

### 4.2 表命名规范

```
{市场}_{数据类型}

市场前缀：
  forex      → 外汇
  stock_cn   → A股
  stock_us   → 美股
  stock_hk   → 港股
  futures_cn → 国内期货
  crypto     → 数字货币

数据类型后缀：
  symbols    → 标的基础信息
  daily      → 日线行情
  hourly     → 小时线行情
  minute     → 分钟线行情
```

**示例**：
| 表名 | 含义 |
|------|------|
| forex_symbols | 外汇标的基础信息 |
| forex_daily | 外汇日线行情 |
| stock_cn_symbols | A股标的基础信息 |
| stock_cn_daily | A股日线行情 |

### 4.3 表结构总览

```
业务系统表（7张）
├── users               用户账户
├── sessions            登录会话
├── markets             市场类型定义
├── datasources         数据源配置
├── collection_tasks    采集任务
├── collection_task_logs 采集日志
└── apscheduler_jobs    定时任务

外汇市场数据表（第一阶段）
├── forex_symbols       外汇标的基础信息
└── forex_daily         外汇日线行情（按年分区）

其他市场数据表（后续阶段按需创建）
├── stock_cn_symbols    A股标的基础信息
├── stock_cn_daily      A股日线行情
├── stock_us_symbols    美股标的基础信息
├── stock_us_daily      美股日线行情
├── futures_cn_symbols  国内期货标的基础信息
├── futures_cn_daily    国内期货日线行情
└── ...（遵循统一设计规范）
```

### 4.4 业务系统表结构

#### markets表（市场类型定义）

```sql
CREATE TABLE markets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,           -- 市场代码（forex, stock_cn）
    name VARCHAR(50) NOT NULL,                   -- 市场名称（外汇, A股）
    description TEXT,                            -- 市场描述
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',-- 市场时区
    is_active BOOLEAN DEFAULT true,              -- 是否启用
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### users表（用户账户）

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt hash
    role VARCHAR(20) NOT NULL DEFAULT 'user',  -- admin/user
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### datasources表（数据源配置）

```sql
CREATE TABLE datasources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    market_id UUID REFERENCES markets(id),       -- 适用市场
    interface VARCHAR(50) NOT NULL,
    description TEXT,
    config_schema JSONB NOT NULL,
    supported_symbols JSONB,
    min_date DATE,
    type VARCHAR(50) NOT NULL DEFAULT 'akshare',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### collection_tasks表（采集任务）

```sql
CREATE TABLE collection_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    datasource_id UUID NOT NULL REFERENCES datasources(id),
    market_id UUID NOT NULL REFERENCES markets(id),  -- 目标市场
    symbol_id UUID NOT NULL,                          -- 目标标的
    start_date DATE,
    end_date DATE,
    cron_expr VARCHAR(100),
    is_enabled BOOLEAN DEFAULT false,
    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    last_status VARCHAR(20),
    last_message TEXT,
    last_records_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 4.5 外汇市场数据表结构（第一阶段）

#### forex_symbols表（外汇标的基础信息）

```sql
CREATE TABLE forex_symbols (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,                -- 货币对代码（USDCNY）
    name VARCHAR(50) NOT NULL,                        -- 货币对名称（中文）
    description TEXT,
    datasource_id UUID REFERENCES datasources(id),
    base_currency VARCHAR(10),                        -- 基础货币（USD）
    quote_currency VARCHAR(10),                       -- 计价货币（CNY）
    is_active BOOLEAN DEFAULT true,
    first_trade_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### forex_daily表（外汇日线行情，按年分区）

```sql
-- 主表定义
CREATE TABLE forex_daily (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol_id UUID NOT NULL REFERENCES forex_symbols(id),
    datasource_id UUID REFERENCES datasources(id),
    date DATE NOT NULL,
    open NUMERIC(10,4),
    high NUMERIC(10,4),
    low NUMERIC(10,4),
    close NUMERIC(10,4),
    change_pct NUMERIC(10,4),
    change_amount NUMERIC(10,4),
    amplitude NUMERIC(10,4),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol_id, date, datasource_id)
) PARTITION BY RANGE (date);

-- 年分区
CREATE TABLE forex_daily_2024 PARTITION OF forex_daily
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE forex_daily_2025 PARTITION OF forex_daily
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE forex_daily_2026 PARTITION OF forex_daily
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE forex_daily_default PARTITION OF forex_daily DEFAULT;
```

### 4.6 其他市场表设计规范（后续阶段参照）

详见 [CODE_STANDARDS.md](CODE_STANDARDS.md) 第1.4节"市场数据表设计规范"。

### 4.7 索引策略

| 表 | 索引 | 类型 | 用途 |
|-----|------|------|------|
| markets | code | B-tree | 市场查询 |
| forex_symbols | code | B-tree | 标的查询 |
| forex_symbols | (datasource_id) | B-tree | 数据源关联 |
| forex_daily | (symbol_id, date) | B-tree复合 | 行情查询 |
| forex_daily | date | B-tree | 时间范围查询 |
| collection_tasks | (market_id) | B-tree | 市场过滤 |
| collection_tasks | (is_enabled) | B-tree | 任务状态查询 |

### 4.3 连接池配置

```python
# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,        # 连接池大小
    max_overflow=20,     # 最大溢出连接
    pool_timeout=30,     # 获取连接超时
    pool_recycle=3600,   # 连接回收时间（秒）
    echo=settings.DEBUG, # SQL日志（调试模式）
)
```

---

## 五、后端服务设计

### 5.1 目录结构

```
backend/app/
├── main.py                 # FastAPI入口
├── config/                 # 配置管理
│   ├── settings.py         # Pydantic Settings
│   └── logging.py          # 日志配置
├── core/                   # 核心模块
│   ├── database.py         # 数据库连接池
│   ├── security.py         # Session认证
│   ├── exceptions.py       # 全局异常处理
│   ├── cache.py            # 内存缓存
│   └── deps.py             # 依赖注入
├── models/                 # SQLAlchemy模型
│   ├── user.py
│   ├── session.py
│   ├── datasource.py
│   ├── collection_task.py
│   └── fx_data.py
├── schemas/                # Pydantic模型
│   ├── user.py
│   ├── auth.py
│   ├── datasource.py
│   ├── collection.py
│   ├── fx_data.py
│   └── common.py           # 统一响应格式
├── api/v1/                 # API路由
│   ├── auth.py             # 认证接口
│   ├── users.py            # 用户管理
│   ├── fx_data.py          # 汇率数据
│   ├── datasource.py       # 数据源管理
│   ├── collection.py       # 采集任务管理
│   └── system.py           # 系统管理
├── services/               # 业务逻辑
│   ├── auth_service.py     # 认证服务
│   ├── user_service.py     # 用户服务
│   ├── fx_service.py       # 汇率数据服务
│   ├── datasource_service.py
│   ├── collection_service.py
│   ├── scheduler_service.py  # APScheduler管理
│   ├── technical_service.py  # TA-Lib技术指标
│   └── cache_service.py    # 缓存服务
├── collectors/             # 数据采集器
│   ├── base.py             # 采集器基类
│   └── akshare_collector.py  # AKShare采集器
└── utils/                  # 工具函数
    ├── technical.py        # 技术指标计算
    └── helpers.py          # 辅助函数
```

### 5.2 API设计规范

#### 统一响应格式

```python
# backend/app/schemas/common.py
from pydantic import BaseModel
from typing import Optional, Any

class Response(BaseModel):
    """统一API响应格式."""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None

class PaginatedResponse(BaseModel):
    """分页响应格式."""
    success: bool
    data: list
    total: int
    page: int
    limit: int
    message: Optional[str] = None
```

#### API路由规范

```python
# 路由命名规范
GET    /api/v1/{resource}          # 列表查询
GET    /api/v1/{resource}/{id}     # 单条查询
POST   /api/v1/{resource}          # 创建
PUT    /api/v1/{resource}/{id}     # 更新
DELETE /api/v1/{resource}/{id}     # 删除

# 特殊操作
POST   /api/v1/auth/login          # 登录
POST   /api/v1/auth/logout         # 登出
PUT    /api/v1/collection/{id}/status  # 任务启停
```

### 5.3 权限检查实现

```python
# backend/app/core/deps.py
from fastapi import Depends, HTTPException
from app.core.security import get_current_user
from app.models.user import User

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    要求admin权限的依赖注入.

    Args:
        current_user: 当前登录用户

    Returns:
        User: admin用户

    Raises:
        HTTPException: 403权限不足
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user
```

### 5.4 APScheduler集成

```python
# backend/app/services/scheduler_service.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

jobstores = {
    'default': SQLAlchemyJobStore(url=settings.DATABASE_URL.replace('+asyncpg', ''))
}

scheduler = AsyncIOScheduler(jobstores=jobstores)

# 启动调度器
scheduler.start()

# 添加任务
scheduler.add_job(
    func=collect_fx_data,
    trigger='cron',
    id='usdcnh_daily',
    **cron_params  # 从可视化配置解析
)
```

---

## 六、前端架构设计

### 6.1 目录结构

```
frontend/src/
├── main.js                 # Vue入口
├── App.vue                 # 根组件
├── router/                 # 路由配置
│   ├── index.js            # 路由实例
│   ├── routes.js           # 路由定义
│   └── guards.js           # 路由守卫
├── stores/                 # Pinia状态管理
│   ├── auth.js             # 认证状态
│   └── fx_data.js          # 汇率数据状态
├── api/                    # API调用
│   ├── index.js            # Axios配置
│   ├── auth.js             # 认证API
│   ├── users.js            # 用户API
│   ├── fx_data.js          # 汇率API
│   ├── datasource.js       # 数据源API
│   └── collection.js       # 采集任务API
├── views/                  # 页面组件
│   ├── Login.vue           # 登录页
│   ├── Dashboard.vue       # 首页
│   ├── FXData.vue          # 数据分析页
│   ├── DataSource.vue      # 数据源管理
│   ├── Collection.vue      # 采集任务管理
│   ├── Users.vue           # 用户管理
│   └── Logs.vue            # 系统日志
├── components/             # 公共组件
│   ├── Navbar.vue          # 导航栏
│   ├── Sidebar.vue         # 侧边栏菜单
│   ├── FXChart.vue         # ECharts图表封装
│   ├── CronBuilder.vue     # 可视化cron配置
│   ├── DataTable.vue       # 数据表格
│   └── Pagination.vue      # 分页组件
├── styles/                 # 样式
│   ├── index.css           # 全局样式
│   └── variables.css       # CSS变量
└── utils/                  # 工具函数
    ├── chart.js            # 图表配置
    ├── format.js           # 数据格式化
    ├── permission.js       # 权限检查
    └── cron.js             # cron解析
```

### 6.2 路由守卫设计

```javascript
// frontend/src/router/guards.js
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 1. 检查是否需要登录
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
    return
  }

  // 2. 检查是否需要admin权限
  if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
    next('/')  // 跳转首页
    return
  }

  // 3. 已登录用户访问登录页
  if (to.path === '/login' && authStore.isLoggedIn) {
    next('/')
    return
  }

  next()
})
```

### 6.3 菜单动态显示

```javascript
// frontend/src/components/Sidebar.vue
const menuItems = computed(() => {
  const authStore = useAuthStore()
  const isAdmin = authStore.user?.role === 'admin'

  return [
    { path: '/fx-data', title: '数据分析', show: true },
    { path: '/datasource', title: '数据源管理', show: isAdmin },
    { path: '/collection', title: '采集任务', show: isAdmin },
    { path: '/users', title: '用户管理', show: isAdmin },
    { path: '/logs', title: '系统日志', show: isAdmin },
  ].filter(item => item.show)
})
```

### 6.4 ECharts图表配置

```javascript
// frontend/src/utils/chart.js
export const klineOption = (data, maData, macdData) => ({
  title: { text: 'USDCNH汇率走势' },
  tooltip: { trigger: 'axis' },
  legend: { data: ['K线', 'MA20', 'MACD'] },
  grid: [
    { left: '10%', right: '8%', height: '50%' },  // K线图
    { left: '10%', right: '8%', top: '65%', height: '20%' },  // MACD图
  ],
  xAxis: [
    { type: 'category', data: data.dates, gridIndex: 0 },
    { type: 'category', data: data.dates, gridIndex: 1 },
  ],
  yAxis: [
    { scale: true, gridIndex: 0 },  // K线Y轴
    { scale: true, gridIndex: 1 },  // MACD Y轴
  ],
  series: [
    { name: 'K线', type: 'candlestick', data: data.klines },
    { name: 'MA20', type: 'line', data: maData },
    { name: 'MACD', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: macdData },
  ],
})
```

### 6.5 可视化Cron配置组件

```vue
<!-- frontend/src/components/CronBuilder.vue -->
<template>
  <el-form>
    <el-form-item label="执行周期">
      <el-select v-model="periodType">
        <el-option label="每天" value="daily" />
        <el-option label="每周" value="weekly" />
        <el-option label="每月" value="monthly" />
        <el-option label="自定义" value="custom" />
      </el-select>
    </el-form-item>

    <el-form-item label="执行时间">
      <el-time-picker v-model="executeTime" />
    </el-form-item>

    <!-- 自定义cron表达式 -->
    <el-form-item v-if="periodType === 'custom'" label="Cron表达式">
      <el-input v-model="cronExpression" />
      <span class="hint">{{ cronDescription }}</span>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { computed } from 'vue'
import { parseCron, generateCron } from '@/utils/cron'

const cronExpression = computed(() => {
  return generateCron(periodType, executeTime)
})
</script>
```

---

## 七、数据采集设计

### 7.1 AKShare采集器

```python
# backend/app/collectors/akshare_collector.py
import akshare as ak
from tenacity import retry, stop_after_attempt, wait_exponential

class AKShareCollector:
    """
    AKShare数据采集器.

    使用AKShare库采集金融数据，支持重试机制.
    """

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def collect_usdcnh(self, start_date: str, end_date: str) -> list:
        """
        采集USDCNH汇率数据.

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            list: 汇率数据列表

        Raises:
            Exception: 采集失败
        """
        df = ak.fx_spot_quote(
            symbol="USDCNH",
            start_date=start_date,
            end_date=end_date
        )
        return df.to_dict('records')
```

### 7.2 APScheduler任务配置

```python
# backend/app/services/scheduler_service.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

class SchedulerService:
    """
    任务调度服务.

    管理APScheduler任务配置和执行.
    """

    def add_collection_task(self, task_id: str, cron_expr: str, callback: callable):
        """
        添加采集任务.

        Args:
            task_id: 任务ID
            cron_expr: cron表达式
            callback: 执行回调函数
        """
        self.scheduler.add_job(
            id=task_id,
            func=callback,
            trigger='cron',
            **self._parse_cron(cron_expr)
        )

    def _parse_cron(self, cron_expr: str) -> dict:
        """
        解析cron表达式为APScheduler参数.

        Args:
            cron_expr: cron表达式 (如 "0 18 * * *")

        Returns:
            dict: APScheduler cron参数
        """
        parts = cron_expr.split()
        return {
            'minute': parts[0],
            'hour': parts[1],
            'day': parts[2],
            'month': parts[3],
            'day_of_week': parts[4],
        }
```

---

## 八、性能优化设计

### 8.1 后端性能优化

| 优化项 | 实现方式 | 效果 |
|--------|---------|------|
| **异步处理** | FastAPI async + SQLAlchemy async | 提升并发能力 |
| **连接池** | asyncpg pool (10+20) | 减少连接开销 |
| **内存缓存** | cachetools TTL缓存 | 减少数据库查询 |
| **批量写入** | 批量insert优化 | 减少写入次数 |
| **索引优化** | 复合索引、时间索引 | 加速查询 |

### 8.2 前端性能优化

| 优化项 | 实现方式 | 效果 |
|--------|---------|------|
| **路由懒加载** | `defineAsyncComponent` | 减少首屏加载 |
| **数据分页** | 默认1000条，30天 | 避免大数据量 |
| **防抖节流** | lodash.debounce | 减少请求频率 |
| **图表优化** | ECharts dataZoom | 大数据渲染优化 |

### 8.3 缓存策略

```python
# backend/app/core/cache.py
from cachetools import TTLCache

# 汇率数据缓存（30天数据，24小时过期）
fx_cache = TTLCache(maxsize=100, ttl=86400)

async def get_cached_fx_data(symbol: str, days: int = 30) -> list:
    """
    获取缓存的汇率数据.

    Args:
        symbol: 汇率符号
        days: 天数

    Returns:
        list: 汇率数据
    """
    cache_key = f"{symbol}_{days}"
    if cache_key in fx_cache:
        return fx_cache[cache_key]

    # 未命中缓存，查询数据库
    data = await query_fx_data(symbol, days)
    fx_cache[cache_key] = data
    return data
```

---

## 九、安全设计

### 9.1 认证安全

| 安全项 | 实现方式 |
|--------|---------|
| **密码存储** | bcrypt hash（rounds=12） |
| **Session存储** | PostgreSQL服务端存储 |
| **Session过期** | 24小时过期，自动清理 |
| **Cookie安全** | HttpOnly, Secure, SameSite |

### 9.2 API安全

| 安全项 | 实现方式 |
|--------|---------|
| **权限检查** | Depends权限注入 |
| **CORS控制** | 白名单限制 |
| **请求超时** | 10秒超时 |
| **错误处理** | 不泄露敏感信息 |

### 9.3 数据安全

| 安全项 | 实现方式 |
|--------|---------|
| **SQL注入防护** | SQLAlchemy参数化查询 |
| **日志脱敏** | 不记录密码、密钥 |
| **配置加密** | 环境变量存储密钥 |

---

## 十、扩展预留设计

### 10.1 数据源扩展

```python
# backend/app/collectors/base.py
class BaseCollector:
    """
    数据采集器基类.

    所有数据源采集器继承此基类.
    """

    async def collect(self, **params) -> list:
        """采集数据（子类实现）."""
        raise NotImplementedError

# 未来可扩展：YahooFinanceCollector, BloombergCollector等
```

### 10.2 告警扩展

```python
# backend/app/services/alert_service.py (预留接口)
class AlertService:
    """
    告警服务（预留）.

    第二阶段实现飞书Webhook推送.
    """

    async def send_alert(self, message: str, channel: str = "feishu"):
        """
        发送告警（预留接口）.

        Args:
            message: 告警消息
            channel: 告警渠道
        """
        # TODO: 第二阶段实现
        pass
```

---

## 十一、部署与运维

### 11.1 本地开发环境

```bash
# 后端开发
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端开发
cd frontend
npm install
npm run dev
```

### 11.2 Docker测试环境

```bash
# 启动测试环境
cd docker
docker-compose up -d

# 查看日志
docker-compose logs -f fdas-app

# 停止环境
docker-compose down
```

### 11.3 数据库迁移

```bash
# 创建迁移
cd backend
alembic revision --autogenerate -m "initial tables"

# 执行迁移
alembic upgrade head
```

---

## 十二、附录

### 12.1 技术栈版本矩阵

| 技术 | 版本 | 备注 |
|------|------|------|
| Python | 3.11 | 类型提示完善 |
| FastAPI | 0.110+ | 异步支持 |
| SQLAlchemy | 2.0+ | Async ORM |
| PostgreSQL | 16 | 最新稳定版 |
| Vue | 3.4+ | Composition API |
| Element Plus | 2.5+ | Vue3组件库 |
| ECharts | 5.5+ | 金融图表 |
| TA-Lib | 0.4.28 | 需C依赖 |

### 12.2 参考文档

- [PRD.md](PRD.md) - 需求设计文档
- [CODE_STANDARDS.md](CODE_STANDARDS.md) - 代码规范文档
- [PERMISSION_DESIGN.md](PERMISSION_DESIGN.md) - 权限设计文档
- [PHASE1_DESIGN.md](PHASE1_DESIGN.md) - 第一阶段设计文档