# 多阶段构建：前端构建阶段
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ ./
RUN npm run build

# 后端运行阶段
FROM python:3.13-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# 创建应用目录
WORKDIR /app

# 复制后端代码
COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# 安装Python依赖
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# 复制Nginx配置
COPY deploy/nginx.conf /etc/nginx/sites-available/default
COPY deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 创建数据目录
RUN mkdir -p /app/data
VOLUME ["/app/data"]

# 暴露端口
EXPOSE 80

# 启动supervisor管理进程
CMD ["/usr/bin/supervisord", "-n"] 