# FDAS Backend Deployment Dockerfile
# 金融数据抓取与分析系统 - 后端部署镜像
# Python 3.13 环境 + TA-Lib支持

# ==================== Stage 1: TA-Lib C库编译 ====================
FROM python:3.13-slim AS talib-builder

WORKDIR /build

# 安装编译工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make wget \
    && rm -rf /var/lib/apt/lists/*

# 编译TA-Lib C库
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib/ \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# ==================== Stage 2: 运行环境 ====================
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
RUN useradd --system --uid 1001 --home-dir /app --shell /usr/sbin/nologin fdas-backend

WORKDIR /app

# 复制依赖文件
COPY requirements.txt ./requirements.txt

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt \
    && pip freeze > requirements.lock

# 复制应用代码
COPY app/ ./app/

# 创建日志和数据目录
RUN mkdir -p logs data \
    && chown -R fdas-backend:fdas-backend /app

# 切换到应用用户
USER fdas-backend

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]