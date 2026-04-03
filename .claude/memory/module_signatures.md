# FDAS模块签名

> 记录已完成模块的关键信息摘要，便于快速恢复上下文而不需重读完整代码。

---

## 项目目录结构

**完成时间**: 2026-04-03

**关键目录**:
```
fdas/
├── backend/app/           # 后端应用
│   ├── config/            # 配置管理(settings.py, logging.py)
│   ├── core/              # 核心模块(database, security, exceptions, cache)
│   ├── models/            # SQLAlchemy模型
│   ├── schemas/           # Pydantic模型
│   ├── api/v1/            # API路由
│   ├── services/          # 业务逻辑
│   ├── collectors/        # 数据采集器
│   └── utils/             # 工具函数
├── frontend/src/          # 前端源码
│   ├── views/             # 页面组件
│   ├── components/        # 公共组件
│   ├── stores/            # Pinia状态
│   ├── router/            # 路由配置
│   ├── api/               # API调用
│   └── styles/            # 样式
├── docker/                # Docker配置
├── docs/                  # 文档
└── .claude/memory/        # Claude记忆
```

**关键文件**:
- `backend/app/main.py`: FastAPI入口，健康检查 `/api/health`
- `backend/app/config/settings.py`: 三层配置(Base/Env/Business)
- `backend/app/config/logging.py`: 日志配置，控制台+文件轮转
- `frontend/src/router/index.js`: 路由配置，含权限守卫
- `frontend/src/stores/auth.js`: Pinia认证状态
- `docker/docker-compose.yml`: fdas-db + fdas-app
- `docker/init-db.sql`: 表结构(users, sessions, datasources, collection_tasks, fx_data, apscheduler_jobs)

**验收**: 目录结构完整，骨架文件创建成功

---

## Claude记忆系统框架

**完成时间**: 2026-04-03

**关键文件**:
- `MEMORY.md`: 记忆索引（<200行），Claude自动加载
- `progress.md`: 开发进度记录，当前模块和下一步任务
- `decisions.md`: 技术决策记录，决策项+原因+应用
- `module_signatures.md`: 模块签名，已完成模块摘要

**使用方式**:
1. Claude启动自动加载MEMORY.md
2. 读取progress.md确认当前进度
3. 按需读取decisions.md了解决策
4. 按需读取module_signatures.md了解已完成模块

**验收**: 四个框架文件创建成功

---

## PRD文档

**完成时间**: 2026-04-03

**文件**: `docs/PRD.md` (~300行)

**核心内容**:
- 项目概述：背景、目标、原则
- 用户角色：admin（全部权限）/ user（数据分析查看）
- 权限矩阵：功能/API/菜单三层权限定义
- 数据流程：采集流程、查询流程、认证流程（含流程图）
- 模块清单：22项模块，优先级、依赖关系
- 第一阶段目标：文档/后端/前端/数据库交付
- 验收标准：功能/性能/安全验收

**关键决策**:
- admin权限：用户管理CRUD、数据源与采集任务管理、系统日志查看、数据访问控制
- 权限控制：前后端双重控制
- 数据量限制：1000条

**验收**: 核心需求、角色、流程、模块清单明确

---

## ARCHITECTURE文档

**完成时间**: 2026-04-03

**文件**: `docs/ARCHITECTURE.md` (~400行)

**核心内容**:
- 六层架构：基础设施→采集→存储→后端→前端→集成
- 技术栈选型：完整清单、版本、选型理由
- 容器架构：前后端合并容器方案
- 数据库设计：6张表DDL、索引策略、连接池配置
- 后端服务设计：目录结构、API规范、权限实现、APScheduler集成
- 前端架构设计：目录结构、路由守卫、菜单显示、ECharts配置、Cron组件
- 数据采集设计：AKShare采集器、APScheduler调度
- 性能优化：后端/前端/缓存策略
- 安全设计：认证/API/数据安全
- 扩展预留：BaseCollector基类、AlertService接口

**关键决策**:
- 容器方案：前后端合并
- 数据库表：users, sessions, datasources, collection_tasks, fx_data, apscheduler_jobs
- 索引：8个索引定义
- 缓存：TTLCache，30天数据

**验收**: 六层架构、技术栈、数据库设计明确

---

## CODE_STANDARDS文档

**完成时间**: 2026-04-03

**文件**: `docs/CODE_STANDARDS.md` (~450行)

**核心内容**:
- 注释规范：Google风格，Python/Vue/JSDoc规范
- 日志规范：格式、级别划分、输出方式、关键操作日志
- 配置规范：三层结构、Pydantic Settings实现
- 性能优化规范：数据库/后端/前端优化要求
- 代码质量规范：文件大小、嵌套深度、命名、类型注解
- Git提交规范：Commit格式、分支规范
- 代码审查清单：功能/质量/注释/日志/安全/性能

**关键决策**:
- 注释风格：Google风格
- 日志格式：`[时间] [级别] [模块名] [请求ID] - 日志内容`
- 日志级别：DEBUG/INFO/WARNING/ERROR/CRITICAL
- 文件大小：Python≤800行，Vue≤500行
- 函数大小：≤50行
- 嵌套深度：≤4层

**验收**: 注释、日志、配置、性能规范明确

---

## PERMISSION_DESIGN文档

**完成时间**: 2026-04-03

**文件**: `docs/PERMISSION_DESIGN.md` (~500行)

**核心内容**:
- 权限模型：RBAC（admin/user两个角色）
- 角色权限矩阵：功能/API/菜单三层矩阵
- Session认证设计：PostgreSQL存储、数据结构、安全配置
- 后端权限控制：Depends依赖注入、全局异常处理
- 前端权限控制：路由守卫、菜单动态显示、权限状态管理
- 安全增强：密码安全、Session清理、登录限制
- 测试用例：后端/前端权限测试

**关键决策**:
- 权限模型：RBAC
- 控制策略：前后端双重控制
- Session存储：PostgreSQL服务端存储
- Session有效期：24小时
- Cookie属性：HttpOnly, Secure, SameSite=Strict
- 密码加密：bcrypt（rounds=12）

**验收**: RBAC模型、Session认证、双重控制明确

---

## PHASE1_DESIGN文档

**完成时间**: 2026-04-03

**文件**: `docs/PHASE1_DESIGN.md` (~600行)

**核心内容**:
- 第一阶段概述：目标、模块清单、开发顺序
- 数据库初始化模块：连接、模型、Alembic迁移
- 配置管理模块：验证脚本
- 日志管理模块：验证脚本
- 用户管理模块：密码服务、用户服务、用户API
- 权限管理模块：依赖注入
- 数据采集模块：AKShare采集器、数据服务、APScheduler调度
- 技术指标模块：MA/MACD计算
- 前端框架模块：布局组件、导航栏组件
- 前端页面模块：登录页、数据可视化、ECharts图表、Cron配置组件
- 集成测试：测试场景、验收标准
- 开发进度跟踪：进度文件更新、中断恢复

**关键实现**:
- SQLAlchemy模型：User, Session, FXData, DataSource, CollectionTask
- Alembic迁移：001_initial.py（6张表）
- AKShare采集器：collect_usdcnh方法
- APScheduler调度：SchedulerService类
- TA-Lib技术指标：calculate_ma, calculate_macd
- 前端组件：Layout, Sidebar, Navbar, FXChart, CronBuilder

**验收**: 所有模块实现思路、验收标准明确

---

<!-- 后续模块签名将在完成后追加 -->