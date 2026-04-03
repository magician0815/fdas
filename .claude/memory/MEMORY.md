# FDAS项目记忆索引

> 此文件由Claude Code自动加载，保持在200行以内。

## 项目概述
- 名称: FDAS（金融数据抓取与分析系统）
- 目标: USDCNH汇率数据采集与可视化
- 技术栈: FastAPI + Vue3 + PostgreSQL + AKShare + ECharts
- 目录: `/Users/chao/.local/bin/Projects/fdas`

## 当前状态
- 阶段: 第一阶段（核心功能实现）
- 真实进度: 约65%
- 状态: 进行中，有遗漏功能待补完
- 详情: [progress.md](progress.md)

## 第一阶段核心验收项（必须完成）

| 功能 | 状态 | 说明 |
|------|------|------|
| 数据实际采集 | ❌ 待完成 | AKShare真实调用，非模拟数据 |
| 数据入库 | ⚠️ 待验证 | 方法存在，需验证真实数据 |
| 定时调度 | ❌ 待完成 | APScheduler配置启动 |
| K线/MA/MACD图表 | ❌ 待完成 | ECharts完整实现 |
| 数据源配置功能 | ❌ 待完成 | Web端可用 |
| 采集任务配置功能 | ❌ 待完成 | Web端可用 |

## 已完成模块

### 后端
- ✅ 数据库模型 + Alembic迁移
- ✅ 配置管理 + 日志管理
- ✅ 全局异常处理
- ✅ 用户认证（登录/登出/Session）
- ✅ 用户CRUD API
- ✅ 权限依赖注入
- ⚠️ AKShare采集器（只返回空数据）
- ⚠️ MA计算（简单实现）
- ❌ MACD计算
- ❌ 数据源管理API
- ❌ 采集任务管理API
- ❌ 系统日志API

### 前端
- ✅ Layout + Sidebar + Navbar组件
- ✅ 登录页面功能
- ⚠️ 数据可视化页面（骨架）
- ⚠️ 数据源管理页面（骨架）
- ⚠️ 采集任务管理页面（骨架）
- ⚠️ 用户管理页面（骨架）
- ⚠️ 系统日志页面（骨架）

## 待完成任务（P0核心）

1. **实现AKShare真实采集** - 调用akshare库获取USDCNH数据
2. **APScheduler配置启动** - 定时调度器
3. **ECharts图表实现** - K线/MA/MACD
4. **数据源管理API+前端** - CRUD功能
5. **采集任务管理API+前端** - CRUD+Cron配置

## 技术决策
| 决策 | 选择 |
|------|------|
| 认证 | Session+Cookie(PostgreSQL) |
| 数据采集 | AKShare |
| 调度 | APScheduler |
| 前端图表 | ECharts |
| 技术指标 | 简单MA（暂不用TA-Lib） |
| 权限控制 | 前后端双重 |

## 关键文件路径
```
docs/PRD.md                  # 需求设计（已更新验收标准）
docs/PHASE1_DESIGN.md        # 第一阶段设计（已更新状态）
.claude/memory/progress.md   # 开发进度（已修正）
backend/app/collectors/      # 采集器（需修改）
backend/app/api/v1/          # API路由
frontend/src/views/          # 前端页面
```

## 下一步任务
**当前**: 实现AKShare真实采集
**目标**: 调用akshare库获取USDCNH真实数据入库