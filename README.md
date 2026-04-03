# FDAS - 金融数据抓取与分析系统

基于全开源技术栈构建的金融数据采集与可视化平台。

## 项目概述

本项目采用分层架构设计，包含数据采集、存储、后端服务、前端展示等核心模块。第一阶段聚焦USDCNH汇率数据的采集与可视化展示。

## 技术栈

### 后端
- FastAPI 0.110+
- SQLAlchemy 2.0 (Async ORM)
- PostgreSQL 16
- AKShare (数据采集)
- TA-Lib (技术指标计算)

### 前端
- Vue 3.4+
- Element Plus 2.5+
- ECharts 5.5+
- Pinia (状态管理)

### 部署
- Docker Desktop
- Docker Compose

## 项目结构

```
fdas/
├── backend/          # 后端服务
├── frontend/         # 前端服务
├── docker/           # Docker配置
├── docs/             # 文档
├── scripts/          # 脚本
└── .claude/          # Claude Code配置
```

## 快速开始

### 1. 启动数据库
```bash
cd docker
docker-compose up fdas-db
```

### 2. 启动后端（开发模式）
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. 启动前端（开发模式）
```bash
cd frontend
npm install
npm run dev
```

## 文档

- [需求设计文档](docs/PRD.md)
- [技术架构文档](docs/ARCHITECTURE.md)
- [代码规范文档](docs/CODE_STANDARDS.md)
- [权限设计文档](docs/PERMISSION_DESIGN.md)
- [第一阶段设计](docs/PHASE1_DESIGN.md)

## 开发进度

详见 [.claude/memory/progress.md](.claude/memory/progress.md)

## License

MIT