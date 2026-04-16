# FDAS多容器部署方案 - Dockerfile
# 金融数据抓取与分析系统 - 应用容器镜像
# 包含: FastAPI后端 + 前端静态文件
# 多阶段构建，优化镜像大小
#
# 关键依赖说明:
# - bcrypt>=4.0.0    : 密码哈希（init-db.sql中admin密码使用bcrypt rounds=12）
# - psycopg2-binary  : APScheduler PostgreSQL同步驱动（asyncpg为异步驱动，不满足APScheduler需求）
# - slowapi>=0.1.9   : API速率限制（login接口必需，参数命名必须为request）
# - TA-Lib           : 技术指标计算库（需编译C库）
#
# 部署注意事项:
# - 前端静态文件复制到/app/static/，需在main.py配置StaticFiles挂载
# - 健康检查依赖curl，已在runtime阶段安装

# ==================== Stage 1: TA-Lib C库编译 ====================
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

# ==================== Stage 3: Python依赖安装 ====================
FROM python:3.13-slim AS deps-builder

COPY --from=talib-builder /usr/lib/libta_lib.* /usr/lib/
COPY --from=talib-builder /usr/include/ta-lib/ /usr/include/
RUN ldconfig

WORKDIR /app
COPY backend/requirements.txt ./requirements.txt

# 安装Python依赖并验证完整性
# pip check确保所有依赖兼容，避免运行时ModuleNotFoundError
RUN pip install --no-cache-dir -r requirements.txt \
    && pip check \
    && pip freeze > requirements.lock

# ==================== Stage 4: 运行环境 ====================
FROM python:3.13-slim AS runtime

# 从talib-builder复制TA-Lib库
COPY --from=talib-builder /usr/lib/libta_lib.* /usr/lib/
COPY --from=talib-builder /usr/include/ta-lib/ /usr/include/
RUN ldconfig

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 创建应用用户
RUN useradd --system --uid 1001 --home-dir /app --shell /usr/sbin/nologin fdas

WORKDIR /app

# 从deps-builder复制Python包
COPY --from=deps-builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=deps-builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY backend/app/ ./app/

# 从frontend-builder复制前端构建产物
COPY --from=frontend-builder /build/frontend/dist ./static/

# 创建日志和数据目录
RUN mkdir -p logs data \
    && chown -R fdas:fdas /app

# 切换到应用用户
USER fdas

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]