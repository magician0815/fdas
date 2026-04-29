# FDAS Frontend Deployment Dockerfile
# 金融数据抓取与分析系统 - 前端部署镜像
# Node.js 20 + Vue 3 + Vite

# ==================== Stage 1: 构建 ====================
FROM node:20-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package.json package-lock.json* ./

# 安装依赖（使用npm ci确保精确版本）
RUN npm ci --prefer-offline --no-audit || npm install

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# 输出目录: /app/dist

# ==================== Stage 2: 运行环境（可选Nginx） ====================
# 如果单独部署前端，可使用Nginx
FROM nginx:alpine AS runtime-nginx

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制Nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动命令
CMD ["nginx", "-g", "daemon off;"]

# ==================== Stage 3: 纯静态文件（用于合并部署） ====================
# 如果合并到后端容器，只需复制dist目录
FROM scratch AS static-only

COPY --from=builder /app/dist /dist

# 此镜像不运行，仅用于导出静态文件