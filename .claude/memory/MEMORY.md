# FDAS项目记忆索引

> 此文件由Claude Code自动加载，保持在200行以内。

## 项目概述
- 名称: FDAS（金融数据抓取与分析系统）
- 目标: 外汇汇率数据采集与可视化
- 技术栈: FastAPI + Vue3 + PostgreSQL + AKShare(forex_hist) + ECharts
- 目录: `/Users/chao/.local/bin/Projects/fdas`

## 当前状态
- 阶段: 第一阶段（核心功能实现）
- 真实进度: 约70%
- 状态: 设计文档更新完成，待执行数据库迁移
- 详情: [progress.md](progress.md)

## 第一阶段核心验收项（必须完成）

| 功能 | 状态 | 说明 |
|------|------|------|
| 数据实际采集 | ❌ 待实现 | 使用AKShare forex_hist接口 |
| 数据入库 | ❌ 待实现 | OHLC + 涨跌幅/涨跌额/振幅 |
| 定时调度 | ❌ 待实现 | APScheduler配置启动 |
| K线/MA/MACD图表 | ❌ 待实现 | ECharts完整实现 |
| 数据源配置功能 | ❌ 待实现 | 配置Schema + 自动获取货币对 |
| 采集任务配置功能 | ❌ 待实现 | 动态表单 + 参数校验 |

## 2026-04-10 更新内容

### 数据库模型更新
- fx_data: 新增symbol_code、change_pct、change_amount、amplitude字段
- datasources: 新增interface、config_schema、supported_symbols、min_date字段
- collection_tasks: 新增symbol、start_date、end_date、last_status等字段
- 新建: collection_task_logs表

### AKShare接口规范
- 接口: `forex_hist` - 外汇日线行情
- 参数: symbol(中文货币对名称)、start_date、end_date
- 返回: OHLC + 涨跌幅 + 涨跌额 + 振幅

### 货币对映射
| 中文 | 英文代码 |
|------|----------|
| 美元人民币 | USDCNY |
| 欧元美元 | EURUSD |
| 英镑美元 | GBPUSD |
| 美元日元 | USDJPY |
| 澳元美元 | AUDUSD |
| ... | ... |

## 已完成模块

### 后端
- ✅ 数据库模型 + Alembic迁移（已更新）
- ✅ 配置管理 + 日志管理
- ✅ 全局异常处理
- ✅ 用户认证（登录/登出/Session）
- ✅ 用户CRUD API
- ✅ 权限依赖注入
- ⚠️ AKShare采集器（设计完成，待实现）
- ⚠️ 数据入库服务（设计完成，待实现）
- ❌ 数据源管理API
- ❌ 采集任务管理API
- ❌ APScheduler调度

### 前端
- ✅ Layout + Sidebar + Navbar组件
- ✅ 登录页面功能
- ⚠️ 数据可视化页面（骨架）
- ⚠️ 数据源管理页面（骨架）
- ⚠️ 采集任务管理页面（骨架）
- ⚠️ 用户管理页面（骨架）
- ⚠️ 系统日志页面（骨架）

## 下一步任务

**当前**: 执行数据库迁移
**目标**: 
1. 创建迁移脚本更新表结构
2. 初始化数据源记录
3. 验证表结构正确

## 技术决策
| 决策 | 选择 |
|------|------|
| 认证 | Session+Cookie(PostgreSQL) |
| 数据采集 | AKShare forex_hist接口 |
| 货币对格式 | 中文名称 + 英文代码同时存储 |
| 调度 | APScheduler |
| 前端图表 | ECharts |
| 技术指标 | MA/MACD（后续考虑TA-Lib） |
| 权限控制 | 前后端双重 |

## 关键文件路径
```
docs/PRD.md                  # 需求设计
docs/PHASE1_DESIGN.md        # 第一阶段设计（已更新）
.claude/memory/progress.md   # 开发进度（已更新）
backend/app/models/          # 数据模型（已更新）
backend/app/collectors/      # 采集器（待实现）
backend/app/api/v1/          # API路由
frontend/src/views/          # 前端页面
```