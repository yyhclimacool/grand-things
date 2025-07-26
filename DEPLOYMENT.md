# 🚀 Grand Things 大事记 - 线上部署指南

本文档提供多种部署方案，你可以根据需求和技术水平选择合适的方案。

## 📋 系统要求

- **服务器**：1GB RAM, 1vCPU, 10GB 硬盘
- **操作系统**：Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **域名**：可选，建议配置

## 🎯 部署方案

### 方案一：Docker 一键部署（推荐） 🐳

**适合**：想要快速部署，不关心细节配置

#### 1. 安装 Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 下载并部署

```bash
# 克隆项目
git clone https://github.com/your-username/grand-things.git
cd grand-things

# 一键部署
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

#### 3. 访问应用

- 🌐 **网站**: http://your-server-ip
- 📚 **API文档**: http://your-server-ip/docs
- 💡 **健康检查**: http://your-server-ip/health

### 方案二：VPS 手动部署 🖥️

**适合**：想要更多控制权，了解服务器配置

#### 1. 准备环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y python3 python3-pip nodejs npm nginx supervisor git curl

# 安装 uv (Python 包管理器)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

#### 2. 部署后端

```bash
# 克隆项目
git clone https://github.com/your-username/grand-things.git
cd grand-things/backend

# 安装依赖
uv sync

# 初始化数据库
uv run init_db.py

# 配置systemd服务
sudo tee /etc/systemd/system/grand-things-api.service > /dev/null <<EOF
[Unit]
Description=Grand Things API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/grand-things/backend
Environment=PATH=/path/to/grand-things/backend/.venv/bin
ExecStart=/path/to/grand-things/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable grand-things-api
sudo systemctl start grand-things-api
```

#### 3. 部署前端

```bash
cd ../frontend

# 安装依赖并构建
npm install
npm run build

# 复制到 nginx 目录
sudo cp -r dist/* /var/www/html/
```

#### 4. 配置 Nginx

```bash
sudo tee /etc/nginx/sites-available/grand-things > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名
    
    location / {
        root /var/www/html;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/grand-things /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 方案三：云平台部署 ☁️

**适合**：不想管理服务器，希望自动扩容

#### 前端部署到 Vercel

1. 前往 [Vercel](https://vercel.com)
2. 连接 GitHub 仓库
3. 设置构建配置：
   - Build Command: `cd frontend && npm run build`
   - Output Directory: `frontend/dist`
   - Root Directory: `/`

#### 后端部署到 Railway/Render

1. 前往 [Railway](https://railway.app) 或 [Render](https://render.com)
2. 连接 GitHub 仓库
3. 设置环境变量：
   ```
   PORT=8000
   DATABASE_URL=sqlite:///app/data/grand_things.db
   ```

## 🔒 配置 HTTPS（可选但推荐）

### 使用 Let's Encrypt

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

## 🛠️ 运维管理

### 常用命令

```bash
# Docker 方式
docker-compose ps              # 查看运行状态
docker-compose logs -f         # 查看日志
docker-compose restart         # 重启服务
docker-compose down            # 停止服务
docker-compose up -d           # 启动服务

# 手动部署方式
sudo systemctl status grand-things-api  # 查看后端状态
sudo systemctl restart nginx            # 重启 nginx
sudo journalctl -u grand-things-api -f  # 查看后端日志
```

### 备份数据

```bash
# Docker 方式
docker-compose exec grand-things cp /app/data/grand_things.db /app/data/backup_$(date +%Y%m%d).db

# 手动方式
cp /path/to/grand-things/backend/grand_things.db /backup/grand_things_$(date +%Y%m%d).db
```

### 更新应用

```bash
# Docker 方式
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 手动方式
git pull
cd frontend && npm run build && sudo cp -r dist/* /var/www/html/
sudo systemctl restart grand-things-api
```

## 🔧 环境变量配置

复制 `deploy/env.example` 为 `.env.production` 并修改：

```bash
# 生成安全密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 修改配置文件
SECRET_KEY=your-generated-secret-key
JWT_SECRET_KEY=your-generated-jwt-secret
ALLOWED_ORIGINS=https://your-domain.com
```

## 🆘 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   sudo lsof -i :80
   sudo kill -9 <PID>
   ```

2. **权限问题**
   ```bash
   sudo chown -R www-data:www-data /var/www/html
   sudo chmod -R 755 /var/www/html
   ```

3. **数据库权限**
   ```bash
   sudo chown -R www-data:www-data /path/to/grand-things/backend/
   ```

### 日志位置

- **Docker**: `docker-compose logs`
- **Nginx**: `/var/log/nginx/error.log`
- **应用**: `sudo journalctl -u grand-things-api`

## 📞 获取帮助

如果遇到问题：

1. 检查日志文件
2. 确认防火墙设置
3. 验证域名解析
4. 查看 [Issues](https://github.com/your-username/grand-things/issues)

---

## 🎉 部署完成后

1. 访问你的网站
2. 创建管理员账户
3. 添加第一个事件
4. 配置主题和个性化设置
5. 邀请朋友使用

**恭喜！你的大事记网站已经成功部署上线！** 🚀 