# FDAS Frontend Dockerfile (构建阶段)
# 金融数据抓取与分析系统 - 前端构建

FROM node:20-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# 输出目录: /app/dist
# 此镜像仅用于构建，最终产物将复制到后端容器