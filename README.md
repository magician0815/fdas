# FDAS - 金融数据抓取与分析系统

基于全开源技术栈构建的金融数据采集与可视化平台。

## 项目概述

本项目采用分层架构设计，包含数据采集、存储、后端服务、前端展示等核心模块。第一阶段聚焦USDCNH汇率数据的采集与可视化展示。

## 技术栈

### 后端
- **Python 3.13+**
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

### 环境要求
- Python 3.13+
- Node.js 18+
- Docker Desktop

### 1. 启动数据库
```bash
cd docker
docker-compose up fdas-db
```

### 2. 启动后端（开发模式）
```bash
cd backend
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. 启动前端（开发模式）
```bash
cd frontend
npm install
npm run dev
```

## ⚠️ 安全警告

### 默认管理员账户

系统初始化时创建默认管理员账户：
- **用户名**: `admin`
- **密码**: `admin123`

**重要**: 生产环境部署后，必须立即通过用户管理界面修改默认密码！

### 环境变量配置

生产环境必须配置以下环境变量：

```bash
# 后端环境变量（.env文件）
SESSION_SECRET=your-secure-random-string-at-least-32-characters
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/fdas
ALLOWED_ORIGINS=https://your-production-domain.com
```

**禁止硬编码密钥或凭据在源代码中！**

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