# FDAS 版本变更日志

## V1.0.0 — 正式首发版本 (2026-07-24)

### 核心功能

- **多市场数据采集**: 外汇/A股/期货/债券/港股/美股/加密货币 7个市场
- **KLineChart v10**: Canvas K线图引擎，27个内置指标 + 15种画线工具
- **MarketProfile**: 声明式市场配置系统，新增市场只需注册配置
- **双源主备**: 外汇(东方财富+BOC)、A股(新浪+腾讯) 自动回退
- **多标的采集**: 一个任务包含多个标的，逐个采集 + 指数退避重试
- **Dashboard**: ECharts 统计图表 + KLineChart K线图
- **权限管理**: bcrypt密码哈希 + Session认证 + slowapi限流 + admin角色

### 部署方案

- **方案A**: 传统Linux服务器裸机部署 (PostgreSQL + Nginx + systemd)
- **方案B**: Docker Desktop 容器化部署 (多容器/单容器)
- **部署脚本**: deploy.sh 一键部署 (含健康检查/环境验证/密钥生成)
- **运维工具**: 备份/恢复/升级/回滚/健康检查/migration

### 技术栈

- 后端: Python 3.13 + FastAPI + SQLAlchemy + APScheduler + AKShare
- 前端: Vue 3 + Vite + KLineChart v10 + ECharts + Element Plus + TypeScript
- 数据库: PostgreSQL 16 (分区表，年度范围分区)
- 测试: 882 后端 + 847 前端 (全部通过)

### 安全加固

- SESSION_SECRET 强制配置 (≥32字符)
- bcrypt 密码哈希 (rounds=12)
- slowapi API限流
- CORS 白名单配置
- session IP校验
- Nginx 安全头 (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)

---

## 版本历史 (迁移前)

FDAS 在 V1.0.0 之前经历了 v2.0.1 → v2.5.0 的迭代周期。
V1.0.0 为全新起点，之前版本不再追溯。
