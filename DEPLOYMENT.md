# FDAS V1.0.0 完整部署手册

> 金融数据抓取与分析系统 (Financial Data Acquisition System)

**版本**: 1.0.0
**更新日期**: 2026-07-24
**适用系统**: Ubuntu 22.04+ / Debian 12+ / CentOS 9+ / macOS (Docker Desktop)

---

## 目录

1. [架构概览](#1-架构概览)
2. [环境要求](#2-环境要求)
3. [方案A: 传统Linux服务器部署](#3-方案a-传统linux服务器部署)
4. [方案B: Docker Desktop 容器化部署](#4-方案b-docker-desktop-容器化部署)
5. [依赖包完整清单](#5-依赖包完整清单)
6. [环境变量参考](#6-环境变量参考)
7. [安全清单](#7-安全清单)
8. [备份与恢复](#8-备份与恢复)
9. [故障排除](#9-故障排除)
10. [附录](#10-附录)

---

## 1. 架构概览

### 1.1 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    用户浏览器                          │
│                 http://host:8000                      │
└────────────────┬────────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │      Nginx (可选)        │  ← 反向代理 / 静态文件服务
    │   端口: 80 → 8000       │
    └────────────┬────────────┘
                 │
    ┌────────────┴────────────┐
    │   FastAPI 后端 (uvicorn) │  ← API + 静态文件
    │      端口: 8000          │
    │   Python 3.13           │
    │   ┌──────────────────┐  │
    │   │ APScheduler      │  │  ← 定时采集调度
    │   │ AKShare 采集器    │  │  ← 金融数据源
    │   │ Session 认证      │  │  ← 管理员登录
    │   └──────────────────┘  │
    └────────────┬────────────┘
                 │
    ┌────────────┴────────────┐
    │   PostgreSQL 16          │  ← 数据库
    │      端口: 5432          │
    │   数据库: fdas           │
    │   用户: fdas             │
    └─────────────────────────┘
```

### 1.2 组件说明

| 组件 | 技术栈 | 说明 |
|------|--------|------|
| 前端 | Vue 3 + Vite + KLineChart v10 + ECharts + Element Plus | SPA 单页应用 |
| 后端 | FastAPI + SQLAlchemy + APScheduler | REST API + 采集调度 |
| 数据库 | PostgreSQL 16 | 7个市场的数据存储 |
| 反向代理 | Nginx (方案A) / 内置静态服务 (方案B) | 静态文件 + API代理 |

### 1.3 两种部署方案对比

| 特性 | 方案A: 传统Linux | 方案B: Docker容器化 |
|------|-----------------|-------------------|
| 适用场景 | 物理服务器/VM | 开发测试/容器化生产 |
| PostgreSQL | 系统安装 | 独立容器 |
| 后端运行 | systemd + uvicorn | Docker容器 |
| 前端服务 | Nginx | 后端内置静态服务 |
| 依赖管理 | 手动安装 | Dockerfile 内置 |
| 升级方式 | 手动替换文件 | 重新构建镜像 |
| TA-Lib | 源码编译 | Dockerfile内编译 |
| 资源占用 | 较低 | 较高(镜像+容器) |
| 部署时间 | 30-60分钟 | 5-10分钟 |

---

## 2. 环境要求

### 2.1 硬件最低配置

| 指标 | 最低要求 | 推荐配置 |
|------|---------|---------|
| CPU | 2核 | 4核+ |
| 内存 | 2GB | 4GB+ |
| 磁盘 | 10GB | 50GB+ (数据增长) |
| 网络 | 可访问互联网(AKShare数据源) | 稳定带宽 |

### 2.2 操作系统要求

**方案A (裸机):**
- Ubuntu 22.04 LTS / 24.04 LTS
- Debian 12 (Bookworm)
- CentOS Stream 9 / RHEL 9+
- Rocky Linux 9+

**方案B (Docker):**
- Linux: 内核 4.x+, Docker Engine 24+
- macOS: macOS 12+, Docker Desktop 4.x+
- Windows: Windows 10/11 Pro, Docker Desktop 4.x+ (WSL2)

### 2.3 端口要求

| 端口 | 服务 | 说明 |
|------|------|------|
| 8000 | 后端 API + 前端 | 面向用户 |
| 5432 | PostgreSQL | 数据库连接 |
| 80 | Nginx (方案A可选) | 可选反向代理 |

---

## 3. 方案A: 传统Linux服务器部署

> **重要**: 以下步骤以 Ubuntu 22.04 为例。其他发行版请替换对应的包管理命令。

### 3.1 系统准备

#### 3.1.1 环境确认

```bash
# 确认操作系统版本
cat /etc/os-release | head -3

# 确认CPU和内存
lscpu | grep "Model name\|CPU(s)"
free -h

# 确认磁盘空间
df -h /

# 确认网络连通性
curl -s -o /dev/null -w "%{http_code}" https://pypi.org
# 预期输出: 200
```

#### 3.1.2 安装系统基础包

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y \
  curl wget git \
  build-essential gcc g++ make \
  libssl-dev libffi-dev \
  libpq-dev \
  nginx \
  postgresql-16 postgresql-client-16 \
  supervisor

# 验证
gcc --version          # 应输出 GCC 版本
nginx -v               # 应输出 nginx/1.x
psql --version         # 应输出 psql (PostgreSQL) 16.x
```

**包来源说明**:

| 包 | 来源 |
|----|------|
| build-essential, libssl-dev, libffi-dev, libpq-dev, nginx, supervisor | Ubuntu 官方 apt 仓库 |
| postgresql-16 | [PostgreSQL Apt Repository](https://www.postgresql.org/download/linux/ubuntu/) |

> PostgreSQL 16 不在 Ubuntu 22.04 默认仓库中，需先添加 APT 源:
> ```bash
> sudo sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
> curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
> sudo apt update
> ```

### 3.2 Python 3.13 安装

#### 3.2.1 环境确认

```bash
# 检查当前Python版本
python3 --version
```

#### 3.2.2 安装

Ubuntu 22.04 默认不包含 Python 3.13，需通过 deadsnakes PPA:

```bash
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.13 python3.13-dev python3.13-venv
```

| 包 | 来源 |
|----|------|
| python3.13, python3.13-dev, python3.13-venv | [deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa) |

#### 3.2.3 验证

```bash
python3.13 --version
# 预期输出: Python 3.13.x
```

### 3.3 TA-Lib C 库编译

AKShare 的技术指标依赖 TA-Lib C 库，需要从源码编译。

#### 3.3.1 环境确认

```bash
which gcc && gcc --version
```

#### 3.3.2 编译安装

```bash
cd /tmp
wget https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make
sudo make install
sudo ldconfig

# 清理
cd /tmp && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
```

| 包 | 版本 | 来源 |
|----|------|------|
| ta-lib | 0.4.0 | [SourceForge](https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/) |

#### 3.3.3 验证

```bash
ls -la /usr/lib/libta_lib.so*
# 预期输出: 存在 libta_lib.so -> libta_lib.so.0 -> libta_lib.so.0.0.0
```

### 3.4 PostgreSQL 配置

#### 3.4.1 环境确认

```bash
sudo systemctl status postgresql
# 预期: active (running)
```

#### 3.4.2 创建数据库和用户

```bash
sudo -u postgres psql <<'SQL'
CREATE USER fdas WITH PASSWORD 'fdas';
CREATE DATABASE fdas OWNER fdas;
GRANT ALL PRIVILEGES ON DATABASE fdas TO fdas;
\c fdas
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
SQL
```

#### 3.4.3 配置客户端认证

编辑 `/etc/postgresql/16/main/pg_hba.conf`，确保包含:

```
# IPv4 local connections
host    all             all             127.0.0.1/32            md5
# Docker network (方案B使用)
host    all             all             172.16.0.0/12           md5
```

```bash
sudo systemctl reload postgresql
```

#### 3.4.4 初始化数据库表结构

```bash
cd /opt/fdas
sudo -u postgres psql -U fdas -d fdas -f docker/init-db.sql
```

#### 3.4.5 验证

```bash
PGPASSWORD=fdas psql -U fdas -d fdas -c "\dt"
# 预期: 列出 17+ 张表 (users, sessions, markets, forex_symbols, ...)

PGPASSWORD=fdas psql -U fdas -d fdas -c "SELECT COUNT(*) FROM markets;"
# 预期: 8

PGPASSWORD=fdas psql -U fdas -d fdas -c "SELECT username, role FROM users;"
# 预期: admin | admin
```

### 3.5 Node.js 安装 (前端构建)

#### 3.5.1 环境确认

```bash
node --version 2>/dev/null || echo "Node.js 未安装"
```

#### 3.5.2 安装 Node.js 20 LTS

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

| 包 | 版本 | 来源 |
|----|------|------|
| nodejs | 20 LTS | [NodeSource](https://github.com/nodesource/distributions) |

#### 3.5.3 验证

```bash
node --version   # 预期: v20.x.x
npm --version    # 预期: 10.x.x
```

### 3.6 后端部署

#### 3.6.1 创建部署目录

```bash
sudo mkdir -p /opt/fdas/backend /opt/fdas/frontend /opt/fdas/logs /opt/fdas/data
sudo chown -R $USER:$USER /opt/fdas
```

#### 3.6.2 创建 Python 虚拟环境

```bash
cd /opt/fdas/backend
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

#### 3.6.3 安装 Python 依赖

```bash
# 复制项目依赖文件
cp /path/to/fdas/backend/requirements.txt .

pip install -r requirements.txt
```

#### 3.6.4 验证依赖安装

```bash
python3.13 -c "
import fastapi; print('fastapi:', fastapi.__version__)
import sqlalchemy; print('sqlalchemy:', sqlalchemy.__version__)
import bcrypt; print('bcrypt:', bcrypt.__version__)
import akshare; print('akshare:', akshare.__version__)
import talib; print('TA-Lib: OK')
import asyncpg; print('asyncpg: OK')
import psycopg2; print('psycopg2: OK')
import slowapi; print('slowapi: OK')
import ccxt; print('ccxt:', ccxt.__version__)
print('所有依赖导入成功')
"
```

#### 3.6.5 配置环境变量

```bash
cd /opt/fdas/backend
cp /path/to/fdas/docker/.env.example .env

# 生成安全密钥
python3.13 -c "import secrets; print(f'SESSION_SECRET={secrets.token_urlsafe(32)}')" >> .env
```

编辑 `.env` 文件:

```ini
DATABASE_URL=postgresql+asyncpg://fdas:fdas@localhost:5432/fdas
SESSION_SECRET=<已生成的安全密钥>
DEBUG=false
ALLOWED_ORIGINS=["http://localhost:8000"]
APP_PORT=8000
```

#### 3.6.6 验证后端启动

```bash
cd /opt/fdas/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 3
curl http://localhost:8000/api/health
# 预期: {"status":"healthy","version":"1.0.0"}
kill %1
```

### 3.7 前端构建与部署

#### 3.7.1 构建前端

```bash
cd /opt/fdas/frontend
cp /path/to/fdas/frontend/package.json .
cp /path/to/fdas/frontend/package-lock.json .
cp -r /path/to/fdas/frontend/src .

npm install
npm run build
```

#### 3.7.2 验证构建产物

```bash
ls dist/index.html && echo "构建成功" || echo "构建失败"
ls dist/assets/ | head -5
```

### 3.8 Nginx 配置 (可选)

如果希望通过 80 端口访问，配置 Nginx 反向代理:

```bash
sudo tee /etc/nginx/sites-available/fdas <<'NGINX'
server {
    listen 80;
    server_name _;

    # 前端静态文件
    root /opt/fdas/frontend/dist;
    index index.html;

    # API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 3600s;
    }

    # Vue SPA 路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/fdas /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 3.9 systemd 服务配置

#### 3.9.1 后端服务

```bash
sudo tee /etc/systemd/system/fdas-backend.service <<'SYSTEMD'
[Unit]
Description=FDAS Backend Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=fdas
Group=fdas
WorkingDirectory=/opt/fdas/backend
EnvironmentFile=/opt/fdas/backend/.env
ExecStart=/opt/fdas/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=append:/opt/fdas/logs/backend.log
StandardError=append:/opt/fdas/logs/backend-error.log

[Install]
WantedBy=multi-user.target
SYSTEMD

sudo useradd -r -s /bin/false fdas 2>/dev/null
sudo systemctl daemon-reload
sudo systemctl enable fdas-backend
sudo systemctl start fdas-backend
```

#### 3.9.2 验证

```bash
sudo systemctl status fdas-backend
# 预期: active (running)

sleep 3
curl http://localhost:8000/api/health
# 预期: {"status":"healthy","version":"1.0.0"}
```

### 3.10 方案A 部署后验证清单

- [ ] `systemctl status fdas-backend` — active
- [ ] `curl http://localhost:8000/api/health` — 返回 `{"status":"healthy","version":"1.0.0"}`
- [ ] `curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'` — 返回 `{"success":true,...}`
- [ ] `curl -s http://localhost:8000/ | head -c 50` — 返回 HTML 页面
- [ ] `PGPASSWORD=fdas psql -U fdas -d fdas -c "\dt"` — 列出 17+ 张表
- [ ] 浏览器访问 `http://服务器IP:8000` — 可登录并使用

---

## 4. 方案B: Docker Desktop 容器化部署

> 方案B提供两种子方案：**多容器**(推荐生产)和**单容器**(简化部署)。

### 4.1 前置条件

#### 4.1.1 环境确认

**Linux:**

```bash
docker --version          # 预期: Docker version 24+
docker compose version     # 预期: Docker Compose version v2+
docker info > /dev/null && echo "Docker daemon OK"
```

**macOS (Docker Desktop):**

```bash
docker --version
docker compose version
docker info > /dev/null && echo "Docker daemon OK"
```

#### 4.1.2 端口和磁盘检查

```bash
# 检查端口占用
ss -tlnp | grep -E "5432|8000" || echo "端口可用"

# 检查磁盘空间
df -h /var/lib/docker 2>/dev/null || df -h ~/Library/Containers/com.docker.docker 2>/dev/null
# 确保 > 5GB 可用
```

#### 4.1.3 Docker 资源检查 (macOS/Windows)

Docker Desktop → Settings → Resources:
- CPUs: ≥ 4
- Memory: ≥ 4 GB
- Disk image size: ≥ 20 GB

### 4.2 多容器方案 (推荐)

架构: `fdas-db` (PostgreSQL 16) + `fdas-app` (FastAPI + 静态文件)

#### 4.2.1 获取部署包

```bash
cd /path/to/fdas/deployment-packages/multi-container
ls -la
# 应包含: docker-compose.yml, Dockerfile.app, deploy.sh, config/, scripts/
```

#### 4.2.2 配置环境变量

```bash
cd /path/to/fdas/deployment-packages/multi-container
cp config/.env.template .env

# 生成 SESSION_SECRET
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# 将输出写入 .env 的 SESSION_SECRET 字段
```

编辑 `.env`:

```ini
DB_PASSWORD=fdas
DB_PORT=5432
SESSION_SECRET=<生成的安全密钥，至少32字符>
DEBUG=false
APP_PORT=8000
ALLOWED_ORIGINS=["http://localhost:8000"]
ENABLE_IP_VALIDATION=false
LOG_LEVEL=INFO
BACKUP_DIR=./backups
```

#### 4.2.3 部署

```bash
# 使用部署脚本 (推荐)
./deploy.sh --action deploy

# 或手动执行
docker compose build
docker compose up -d
```

**deploy.sh 流程说明:**
1. 环境检查 (Docker版本, 磁盘空间)
2. `.env` 配置验证 (SESSION_SECRET长度)
3. 构建镜像 (多阶段构建: TA-Lib + 前端 + 依赖 + 运行时)
4. 启动容器 (DB → 等待就绪 → App)
5. 数据库初始化 (init-db.sql)
6. 健康检查 (重试机制)
7. 显示访问地址

首次构建耗时约 8-15 分钟(TA-Lib编译)。后续构建使用 Docker 缓存约 1-2 分钟。

#### 4.2.4 验证

```bash
# 容器状态
docker compose ps
# 预期: fdas-db (healthy), fdas-app (healthy)

# 数据库
docker exec fdas-db pg_isready -U fdas
# 预期: /var/run/postgresql:5432 - accepting connections

# API 健康检查
curl http://localhost:8000/api/health
# 预期: {"status":"healthy","version":"1.0.0"}

# 登录测试
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# 预期: {"success":true,"data":{"user":{...}}}

# 前端
curl -s http://localhost:8000/ | head -c 50
# 预期: <!DOCTYPE html>...
```

### 4.3 单容器方案

所有服务 (PostgreSQL + Nginx + uvicorn) 在一个容器内通过 supervisord 管理。

#### 4.3.1 配置与部署

```bash
cd /path/to/fdas/deployment-packages/single-container
cp config/.env.template .env
# 编辑 .env (同上)

./deploy.sh --action deploy
```

#### 4.3.2 验证

```bash
# 检查 supervisord 管理的进程
docker exec fdas-all supervisorctl status
# 预期:
#   postgresql    RUNNING
#   fdas_backend  RUNNING
#   nginx         RUNNING

# API 健康检查
curl http://localhost:8000/api/health
```

### 4.4 常用运维命令 (Docker)

```bash
# 多容器
docker compose ps                          # 查看容器状态
docker compose logs -f --tail=50 fdas-app  # 应用日志
docker compose restart                     # 重启
docker compose down                        # 停止并移除容器
docker compose down -v                     # 停止并移除容器+卷(数据丢失!)

# 单容器
docker exec -it fdas-all supervisorctl restart fdas_backend  # 重启后端
docker exec -it fdas-all psql -U fdas -d fdas                # 进入数据库
docker logs -f fdas-all                                      # 查看日志
```

### 4.5 macOS 特别说明

Docker Desktop macOS 使用 `osxfs` 卷挂载，存在缓存延迟问题。更新前端后：

```bash
docker compose restart fdas-app
# 或完全重建:
docker compose down && docker compose build --no-cache && docker compose up -d
```

### 4.6 方案B 部署后验证清单

- [ ] `docker compose ps` — 所有容器 healthy
- [ ] `curl http://localhost:8000/api/health` — version: "1.0.0"
- [ ] `curl -X POST .../api/v1/auth/login -d '{"username":"admin","password":"admin123"}'` — success: true
- [ ] `docker exec fdas-db pg_isready -U fdas` — accepting connections
- [ ] 浏览器访问 `http://localhost:8000` — 可登录并使用
- [ ] `docker exec fdas-db psql -U fdas -d fdas -c "SELECT COUNT(*) FROM markets"` — 8

---

## 5. 依赖包完整清单

### 5.1 系统级依赖

| 包 | 版本 | 用途 | 来源 (Ubuntu) | 方案A | 方案B |
|----|------|------|-------------|-------|-------|
| build-essential | — | C编译工具链 | apt (官方) | 必需 | — |
| libssl-dev | — | SSL/TLS加密 | apt (官方) | 必需 | — |
| libffi-dev | — | FFI接口 | apt (官方) | 必需 | — |
| libpq-dev | — | PostgreSQL客户端库 | apt (官方) | 必需 | — |
| gcc/g++ | 11+ | C/C++编译器 | apt (官方) | 必需 | — |
| make | 4+ | 构建工具 | apt (官方) | 必需 | — |
| wget | — | 文件下载 | apt (官方) | 必需 | — |
| curl | 7+ | HTTP客户端(健康检查) | apt (官方) | 必需 | 内置 |
| nginx | 1.24+ | Web服务器/反向代理 | apt (官方) | 推荐 | — |
| supervisor | 4+ | 进程管理 | apt (官方) | 可选 | 单容器 |
| TA-Lib C | 0.4.0 | 技术指标库 | [SourceForge](https://sourceforge.net/projects/ta-lib/) | 必需 | Dockerfile内 |
| PostgreSQL | 16 | 数据库 | [PostgreSQL APT](https://apt.postgresql.org/) | 必需 | 镜像 |
| Python | 3.13+ | 运行时 | [deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa) | 必需 | 镜像 |
| Node.js | 20 LTS | 前端构建 | [NodeSource](https://github.com/nodesource/distributions) | 必需 | Dockerfile内 |

### 5.2 Python 依赖 (PyPI)

| 包 | 版本要求 | 用途 |
|----|---------|------|
| fastapi | >=0.110.0 | Web框架 |
| uvicorn[standard] | >=0.27.0 | ASGI服务器 |
| sqlalchemy[asyncio] | >=2.0.0 | 异步ORM |
| asyncpg | >=0.29.0 | PostgreSQL异步驱动 |
| psycopg2-binary | >=2.9.0 | PostgreSQL同步驱动 |
| alembic | >=1.13.0 | 数据库迁移 |
| pydantic | >=2.5.0 | 数据校验 |
| pydantic-settings | >=2.1.0 | 配置管理 |
| itsdangerous | >=2.1.0 | 会话签名 |
| starlette-session | >=0.3.0 | 服务端Session |
| bcrypt | >=4.0.0 | 密码哈希 |
| slowapi | >=0.1.9 | API限流 |
| akshare | >=1.12.0 | 金融数据采集 |
| apscheduler | >=3.10.0 | 定时任务调度 |
| tenacity | >=8.2.0 | 重试机制 |
| TA-Lib | >=0.4.28 | 技术分析指标 |
| pandas | >=2.0.0 | 数据处理 |
| numpy | >=1.24.0 | 数值计算 |
| cachetools | >=5.3.0 | 缓存工具 |
| ccxt | >=4.0.0 | 加密货币数据 |
| httpx | >=0.26.0 | HTTP客户端 |

来源: [PyPI](https://pypi.org/) (通过 `pip install`)

### 5.3 Node.js 依赖 (npm)

| 包 | 版本 | 用途 |
|----|------|------|
| vue | ^3.4.0 | 前端框架 |
| vue-router | ^4.2.0 | 路由 |
| pinia | ^2.1.0 | 状态管理 |
| element-plus | ^2.5.0 | UI组件库 |
| @element-plus/icons-vue | ^2.3.0 | 图标 |
| axios | ^1.6.0 | HTTP客户端 |
| echarts | ^5.5.0 | 统计图表 |
| klinecharts | ^10.0.0 | K线图引擎 |
| mathjs | ^15.2.0 | 数学计算 |
| vue-i18n | ^9.9.0 | 国际化 |

来源: [npm registry](https://www.npmjs.com/) (通过 `npm install`)

### 5.4 Docker 镜像

| 镜像 | 来源 | 用途 |
|------|------|------|
| python:3.13-slim | Docker Hub | 后端运行时 |
| postgres:16-alpine | Docker Hub | 数据库 |
| node:20-alpine | Docker Hub | 前端构建 |
| nginx:alpine | Docker Hub | 前端服务(单容器) |

---

## 6. 环境变量参考

### 6.1 后端环境变量

| 变量 | 必填 | 默认值 | 说明 | 方案A | 方案B |
|------|------|--------|------|-------|-------|
| DATABASE_URL | 是 | `postgresql+asyncpg://fdas:fdas@localhost:5432/fdas` | 数据库连接字符串 | ✓ | ✓ |
| SESSION_SECRET | 是 | 无 | 会话签名密钥(≥32字符) | ✓ | ✓ |
| DEBUG | 否 | `false` | 调试模式 | ✓ | ✓ |
| ALLOWED_ORIGINS | 否 | `["http://localhost:3000","http://localhost:8080"]` | CORS白名单(JSON数组) | ✓ | ✓ |
| APP_PORT | 否 | `8000` | 应用监听端口 | ✓ | ✓ |
| ENABLE_IP_VALIDATION | 否 | `false` | 是否启用IP校验 | ✓ | ✓ |
| LOG_LEVEL | 否 | `INFO` | 日志级别(DEBUG/INFO/WARNING/ERROR) | ✓ | ✓ |
| CACHE_TTL_SECONDS | 否 | `300` | 缓存TTL | ✓ | ✓ |
| DEFAULT_COLLECTION_CRON | 否 | `0 6 * * *` | 默认采集Cron | ✓ | ✓ |
| WS_HEARTBEAT_INTERVAL | 否 | `30` | WebSocket心跳间隔(秒) | ✓ | ✓ |
| WS_RECONNECT_MAX_DELAY | 否 | `30` | WebSocket重连最大延迟(秒) | ✓ | ✓ |

### 6.2 数据库环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| DB_PASSWORD | 否 | `fdas` | 数据库密码 |
| DB_PORT | 否 | `5432` | 数据库端口 |
| POSTGRES_USER | 否 | `fdas` | 数据库用户 |
| POSTGRES_DB | 否 | `fdas` | 数据库名 |
| POSTGRES_PASSWORD | 否 | `fdas` | 数据库密码(镜像) |

### 6.3 SESSION_SECRET 生成

```bash
# 方式1: Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 方式2: OpenSSL
openssl rand -base64 32

# 方式3: /dev/urandom
cat /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c 32
```

---

## 7. 安全清单

### 7.1 必须配置 (CRITICAL)

- [ ] **SESSION_SECRET**: 设置≥32字符的随机密钥，禁止默认值
- [ ] **管理员密码**: 首次登录后立即修改 (默认: `admin/admin123`)
- [ ] **数据库密码**: 修改默认 `fdas` 密码

```sql
-- 修改数据库密码
ALTER USER fdas WITH PASSWORD '<新密码>';
-- 同步更新 .env 中的 DATABASE_URL
```

- [ ] **CORS配置**: `ALLOWED_ORIGINS` 限制为实际访问域名

### 7.2 推荐配置

- [ ] 启用防火墙，仅开放必要端口

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP (如使用Nginx)
sudo ufw allow 8000/tcp  # 直接访问
sudo ufw deny 5432/tcp   # 禁止数据库外部访问
sudo ufw enable
```

- [ ] 使用 HTTPS (通过 Nginx + Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

- [ ] 禁用 DEBUG 模式 (`DEBUG=false`)
- [ ] 启用 IP 校验 (`ENABLE_IP_VALIDATION=true`)
- [ ] 定期更新依赖: `pip list --outdated`

### 7.3 默认凭据 (部署后务必修改)

| 服务 | 用户名 | 默认密码 | 修改方式 |
|------|--------|---------|---------|
| Web 管理 | admin | admin123 | 登录后个人设置 |
| PostgreSQL | fdas | fdas | `ALTER USER fdas WITH PASSWORD '...'` |

---

## 8. 备份与恢复

### 8.1 方案A (裸机) 备份

```bash
# 全量备份
pg_dump -U fdas -d fdas -F c -f /opt/fdas/backups/fdas_$(date +%Y%m%d_%H%M%S).dump

# 仅数据备份
pg_dump -U fdas -d fdas --data-only -F c -f /opt/fdas/backups/fdas_data_$(date +%Y%m%d).dump

# 设置 cron 定时备份 (每日凌晨2点)
echo "0 2 * * * pg_dump -U fdas -d fdas -F c -f /opt/fdas/backups/fdas_\$(date +\%Y\%m\%d).dump" | crontab -
```

### 8.2 方案B (Docker) 备份

```bash
# 使用部署包脚本
cd /path/to/fdas/deployment-packages/multi-container
./deploy.sh --action backup

# 手动备份
docker exec fdas-db pg_dump -U fdas -d fdas -F c > fdas_backup_$(date +%Y%m%d).dump
```

### 8.3 恢复

```bash
# 方案A
pg_restore -U fdas -d fdas -c /path/to/backup.dump

# 方案B
docker exec -i fdas-db pg_restore -U fdas -d fdas -c < /path/to/backup.dump
```

---

## 9. 故障排除

### 9.1 常见错误

| 症状 | 可能原因 | 解决方案 |
|------|---------|---------|
| `ModuleNotFoundError: bcrypt` | Python 3.13不兼容旧版bcrypt | `pip install bcrypt>=4.0.0` |
| `ModuleNotFoundError: psycopg2` | psycopg2-binary未安装 | `pip install psycopg2-binary>=2.9.0` |
| `ImportError: libta_lib.so` | TA-Lib C库未安装 | 重新编译TA-Lib，确认 `ldconfig` |
| `SESSION_SECRET not configured` | 环境变量未设置 | 检查 `.env` 文件中的 SESSION_SECRET |
| `Connection refused` 连数据库 | PostgreSQL未启动或端口错误 | `systemctl status postgresql` / `docker compose ps` |
| 前端 404 错误 | dist目录不存在或Nginx配置错误 | 检查构建产物 `ls frontend/dist/` |
| 容器启动即退出 | 端口冲突 | 检查 5432/8000 端口占用 |
| AKShare API 超时 | 网络问题或API限流 | 等待重试，检查网络连通性 |
| 前端页面白屏 | JS文件404，nginx未正确代理 | 检查 nginx 配置，确认 API 请求路径 |
| APScheduler 错误 | 时区或pickle序列化问题 | 确认容器/系统时区为 UTC |

### 9.2 日志查看

```bash
# 方案A
sudo journalctl -u fdas-backend -f            # 后端日志
sudo tail -f /opt/fdas/logs/backend.log       # 应用日志
sudo tail -f /var/log/postgresql/postgresql-*.log  # 数据库日志

# 方案B
docker compose logs -f fdas-app               # 应用日志
docker compose logs -f fdas-db                # 数据库日志
```

---

## 10. 附录

### 附录A: 命令速查表

```bash
# === 后端 ===
cd /opt/fdas/backend && source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload  # 开发模式
python -m pytest tests/ -q --tb=short                       # 运行测试

# === 前端 ===
cd /opt/fdas/frontend
npm run dev          # 开发服务器 (端口3000)
npm run build        # 生产构建
npm run test         # 运行测试

# === 数据库 ===
psql -U fdas -d fdas                                                # 连接
\dt                                                                 # 列出表
SELECT COUNT(*) FROM forex_daily;                                   # 数据量统计
SELECT schemaname,relname,n_live_tup FROM pg_stat_user_tables;      # 表统计

# === Docker ===
docker compose up -d           # 启动
docker compose down            # 停止
docker compose build --no-cache # 无缓存重建
docker compose logs -f          # 查看日志
docker system prune -a          # 清理未使用的镜像/容器/卷

# === systemd ===
sudo systemctl start/stop/restart fdas-backend
sudo systemctl status fdas-backend
sudo journalctl -u fdas-backend -f

# === Git ===
git log --oneline -10
git tag -l
git stash && git pull
```

### 附录B: 文件路径参考

```
项目根目录/
├── VERSION                    # 版本文件 (1.0.0)
├── DEPLOYMENT.md              # 本部署手册
├── CLAUDE.md                  # Claude Code 项目配置
├── README.md                  # 项目说明
├── .gitignore                 # Git 忽略规则
├── docker/
│   ├── docker-compose.yml     # 开发环境 Docker Compose
│   ├── init-db.sql            # 数据库初始化脚本
│   └── .env.example           # 环境变量模板
├── backend/
│   ├── app/main.py            # FastAPI 应用入口
│   ├── requirements.txt       # Python 依赖列表
│   └── tests/                 # 后端测试
├── frontend/
│   ├── package.json           # Node 依赖
│   ├── vite.config.js         # Vite 构建配置
│   └── src/                   # 前端源码
├── docs/                      # 设计文档
│   ├── ARCHITECTURE.md        # 技术架构
│   ├── PRD.md                 # 产品需求
│   └── deployment/
│       └── OPERATION.md       # 运维操作手册
├── deployment-packages/       # 部署包
│   ├── multi-container/       # 多容器方案
│   ├── single-container/      # 单容器方案
│   ├── backend/               # 后端组件
│   ├── database/              # 数据库组件
│   ├── frontend/              # 前端组件
│   └── update/                # 升级框架
└── deployment/                # 部署模板
    └── systemd/               # systemd unit 模板
```

**方案A 部署路径:**

```
/opt/fdas/
├── backend/
│   ├── app/            # 后端源码
│   ├── venv/           # Python虚拟环境
│   └── .env            # 环境变量
├── frontend/
│   ├── src/            # 前端源码
│   └── dist/           # 构建产物
├── logs/               # 日志目录
├── data/               # 数据目录
└── backups/            # 备份目录
```

### 附录C: 数据库表清单

| 表名 | 说明 | 记录数(初始) |
|------|------|------------|
| `users` | 用户表 | 1 (admin) |
| `sessions` | 会话表 | 0 |
| `markets` | 市场定义 | 8 |
| `datasources` | 数据源配置 | 6 |
| `collection_tasks` | 采集任务 | 0 |
| `collection_task_logs` | 采集日志 | 0 |
| `forex_symbols` | 外汇标的 | 20 |
| `forex_daily` | 外汇日线 | 0 (分区表) |
| `stock_symbols` | 股票标的 | 6073 |
| `stock_daily` | 股票日线 | 0 (分区表) |
| `futures_varieties` | 期货品种 | 5 |
| `futures_contracts` | 期货合约 | 0 |
| `futures_daily` | 期货日线 | 0 (分区表) |
| `bond_symbols` | 债券标的 | 0 |
| `bond_daily` | 债券日线 | 0 (分区表) |
| `apscheduler_jobs` | 调度器状态 | 0 |
| `user_chart_settings` | 用户图表设置 | 0 |
| `datasource_wizard_sessions` | 数据源向导 | 0 |

### 附录D: systemd Unit 文件模板

文件位置: `deployment/systemd/`

**fdas-backend.service:**

```ini
[Unit]
Description=FDAS Backend Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=fdas
Group=fdas
WorkingDirectory=/opt/fdas/backend
EnvironmentFile=/opt/fdas/backend/.env
ExecStart=/opt/fdas/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=append:/opt/fdas/logs/backend.log
StandardError=append:/opt/fdas/logs/backend-error.log

[Install]
WantedBy=multi-user.target
```

**fdas-scheduler.service:** (可选，如需要独立调度进程)

```ini
[Unit]
Description=FDAS Scheduler Service
After=fdas-backend.service
Requires=fdas-backend.service

[Service]
Type=simple
User=fdas
Group=fdas
WorkingDirectory=/opt/fdas/backend
EnvironmentFile=/opt/fdas/backend/.env
ExecStart=/opt/fdas/backend/venv/bin/python -c "from app.services.scheduler_service import scheduler_service; scheduler_service.start()"
Restart=always
RestartSec=10
StandardOutput=append:/opt/fdas/logs/scheduler.log
StandardError=append:/opt/fdas/logs/scheduler-error.log

[Install]
WantedBy=multi-user.target
```

---

> **文档结束** — FDAS V1.0.0 完整部署手册
>
> 如有问题请查阅 `docs/deployment/OPERATION.md` 获取更多运维细节。
