# FDAS单容器部署方案 - Dockerfile
# 金融数据抓取与分析系统 - 全服务容器镜像
# 包含: PostgreSQL + FastAPI后端 + Nginx前端
# 用户隔离: postgres(UID 999), fdas-backend(UID 1001), fdas-frontend(UID 1002)

# ==================== Stage 1: TA-Lib编译 ====================
FROM python:3.13-slim AS talib-builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make wget \
    && rm -rf /var/lib/apt/lists/*

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib/ \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# ==================== Stage 2: 前端构建 ====================
FROM node:20-alpine AS frontend-builder

WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --prefer-offline --no-audit || npm install
COPY frontend/ ./
RUN npm run build

# ==================== Stage 3: 运行环境 ====================
FROM python:3.13-slim AS runtime

# 从talib-builder复制TA-Lib库
COPY --from=talib-builder /usr/lib/libta_lib.* /usr/lib/
COPY --from=talib-builder /usr/include/ta-lib/ /usr/include/
RUN ldconfig

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    # PostgreSQL
    postgresql postgresql-contrib \
    # Nginx
    nginx \
    # Supervisor进程管理
    supervisor \
    # 工具
    curl procps net-tools \
    && rm -rf /var/lib/apt/lists/*

# ==================== 用户创建 ====================
# postgres用户（PostgreSQL官方镜像默认UID 999）
RUN useradd --system --uid 999 --home-dir /var/lib/postgresql \
    --shell /usr/sbin/nologin postgres || true

# fdas-backend用户
RUN useradd --system --uid 1001 --home-dir /opt/fdas/backend \
    --shell /usr/sbin/nologin fdas-backend

# fdas-frontend用户
RUN useradd --system --uid 1002 --home-dir /opt/fdas/frontend \
    --shell /usr/sbin/nologin fdas-frontend

# ==================== 目录创建 ====================
RUN mkdir -p /opt/fdas/backend/app \
    && mkdir -p /opt/fdas/frontend/dist \
    && mkdir -p /opt/fdas/config \
    && mkdir -p /var/log/fdas \
    && mkdir -p /var/lib/postgresql/data \
    && mkdir -p /var/run/postgresql \
    && mkdir -p /var/run/supervisor

# ==================== 安装Python依赖 ====================
WORKDIR /opt/fdas/backend
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && pip freeze > requirements.lock

# ==================== 复制应用代码 ====================
COPY backend/app/ ./app/

# ==================== 复制前端构建产物 ====================
COPY --from=frontend-builder /build/frontend/dist /opt/fdas/frontend/dist

# ==================== 复制数据库初始化脚本 ====================
COPY docker/init-db.sql /opt/fdas/config/init-db.sql

# ==================== 复制Supervisor配置 ====================
COPY deployment-packages/single-container/config/supervisord.conf /opt/fdas/config/supervisord.conf

# ==================== 复制Nginx配置 ====================
COPY deployment-packages/single-container/config/nginx.conf /etc/nginx/sites-available/fdas
RUN ln -sf /etc/nginx/sites-available/fdas /etc/nginx/sites-enabled/fdas \
    && rm -f /etc/nginx/sites-enabled/default

# ==================== 设置权限 ====================
RUN chown -R fdas-backend:fdas-backend /opt/fdas/backend \
    && chown -R fdas-frontend:fdas-frontend /opt/fdas/frontend \
    && chown -R postgres:postgres /var/lib/postgresql /var/run/postgresql \
    && chown -R root:root /opt/fdas/config \
    && chmod 600 /opt/fdas/config/*.conf

# ==================== 健康检查 ====================
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# ==================== 暴露端口 ====================
EXPOSE 8000 5432

# ==================== 启动命令 ====================
CMD ["supervisord", "-c", "/opt/fdas/config/supervisord.conf"]