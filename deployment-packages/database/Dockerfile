# FDAS Database Deployment Dockerfile
# 金融数据抓取与分析系统 - 数据库部署镜像
# PostgreSQL 16

FROM postgres:16-alpine

# 维护者信息
LABEL maintainer="FDAS Team"
LABEL description="FDAS PostgreSQL数据库镜像"
LABEL version="2.0.1"

# 设置环境变量
ENV POSTGRES_USER=fdas
ENV POSTGRES_DB=fdas

# 复制初始化脚本
COPY init-db.sql /docker-entrypoint-initdb.d/init-db.sql

# 复制配置文件（可选）
COPY config/postgresql.conf /etc/postgresql/postgresql.conf
COPY config/pg_hba.conf /etc/postgresql/pg_hba.conf

# 数据目录
ENV PGDATA=/var/lib/postgresql/data/pgdata

# 健康检查
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=5 \
    CMD pg_isready -U fdas -d fdas || exit 1

# 暴露端口
EXPOSE 5432

# 启动命令（使用自定义配置）
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]