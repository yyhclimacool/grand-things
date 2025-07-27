# 📖 Grand Things 本地开发指南

本指南介绍如何在本地环境中设置和运行 Grand Things 后端应用。

## 🛠️ 环境要求

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) - 现代化的 Python 包管理器
- Docker & Docker Compose
- Git

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/grand-things.git
cd grand-things/backend
```

### 2. 安装 uv

如果还未安装 uv，请先安装：

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或者使用 pip
pip install uv

# 验证安装
uv --version
```

### 3. 启动 PostgreSQL 数据库

使用 Docker Compose 启动本地 PostgreSQL 数据库：

```bash
# 启动数据库服务
docker compose -f docker-compose.dev.yml up -d postgres

# 查看服务状态
docker compose -f docker-compose.dev.yml ps
```

这将启动：

- **PostgreSQL 16**: 端口 5432，数据库名 `grand_things`
- **pgAdmin 4**: 端口 8080，Web管理界面

### 4. 配置环境变量

复制并编辑环境变量文件：

```bash
cp env.dev.example .env.dev
```

编辑 `.env.dev` 文件：

```bash
# 数据库配置（使用 Docker Compose）
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/grand_things

# 应用配置
RAILWAY_ENVIRONMENT=development
SECRET_KEY=your-development-secret-key
JWT_SECRET_KEY=your-development-jwt-key

# 跨域配置（前端地址）
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 5. 安装项目依赖

```bash
# 使用 uv 同步依赖（自动创建虚拟环境）
uv sync

# 如果需要添加新依赖
uv add package_name

# 如果需要开发依赖
uv add --dev package_name
```

### 6. 初始化数据库

```bash
# 使用 uv 运行数据库初始化脚本
uv run python init_db.py
```

你应该看到类似的输出：

```
🚀 开始 PostgreSQL 数据库初始化...
📍 数据库URL: postgresql://postgres:postgres@localhost:5432/grand_things
🐘 检测到 PostgreSQL 数据库
🔗 测试数据库连接...
✅ 数据库连接成功
📊 PostgreSQL 版本: PostgreSQL 16.x ...
🏗️  开始创建数据库表结构...
✅ 数据库初始化成功
🎉 PostgreSQL 数据库初始化完成
```

### 7. 启动应用

```bash
# 设置环境变量并启动应用
export $(cat .env.dev | grep -v '^#' | xargs)
uv run python main.py

# 或者使用一行命令
export $(cat .env.dev | grep -v '^#' | xargs) && uv run python main.py
```

应用将在 <http://localhost:8000> 启动。

## 🗄️ 数据库管理

### 使用 pgAdmin

1. 访问 <http://localhost:8080>
2. 登录信息：
   - Email: `admin@grandthings.dev`
   - Password: `admin123`

3. 添加服务器连接：
   - Host: `postgres` (Docker网络内) 或 `localhost`
   - Port: `5432`
   - Database: `grand_things`
   - Username: `postgres`
   - Password: `postgres`

### 使用命令行

```bash
# 连接到 PostgreSQL
docker exec -it grand-things-postgres psql -U postgres -d grand_things

# 查看表结构
\dt

# 查看用户表
SELECT * FROM users;

# 查看事件表
SELECT * FROM events;
```

## 🔄 开发工作流

### 日常开发

```bash
# 启动数据库（如果未运行）
docker compose -f docker-compose.dev.yml up -d postgres

# 同步依赖（如果有更新）
uv sync

# 设置环境变量并启动应用
export $(cat .env.dev | grep -v '^#' | xargs)
uv run python main.py
```

### 重置数据库

```bash
# 停止并删除数据库容器（会清空数据）
docker compose -f docker-compose.dev.yml down -v

# 重新启动数据库
docker compose -f docker-compose.dev.yml up -d postgres

# 重新初始化数据库
uv run python init_db.py
```

### 查看日志

```bash
# 查看数据库日志
docker compose -f docker-compose.dev.yml logs postgres

# 查看 pgAdmin 日志
docker compose -f docker-compose.dev.yml logs pgadmin

# 实时查看日志
docker compose -f docker-compose.dev.yml logs -f postgres
```

## 🧪 测试

```bash
# 运行测试（如果有）
uv run pytest

# 测试数据库连接
uv run python -c "from app.database import engine; print('✅ 连接成功' if engine.connect() else '❌ 连接失败')"

# 测试API健康检查
curl http://localhost:8000/health
```

## 📝 API 文档

启动应用后，访问以下地址查看API文档：

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## 🔧 故障排除

### 数据库连接问题

```bash
# 检查 PostgreSQL 是否运行
docker compose -f docker-compose.dev.yml ps postgres

# 检查端口是否被占用
lsof -i :5432

# 重启数据库服务
docker compose -f docker-compose.dev.yml restart postgres
```

### 应用启动问题

```bash
# 检查 Python 依赖
uv pip check

# 查看详细错误信息
uv run python main.py --verbose

# 检查环境变量
env | grep -E "(DATABASE_URL|SECRET_KEY)"

# 检查 uv 环境
uv pip list
```

### 权限问题

```bash
# 检查数据库权限
docker exec -it grand-things-postgres psql -U postgres -c "\du"

# 重置 pgAdmin 权限
docker compose -f docker-compose.dev.yml down pgadmin
docker volume rm grand-things_pgadmin_data
docker compose -f docker-compose.dev.yml up -d pgadmin
```

## 🌟 开发技巧

1. **使用 VS Code PostgreSQL 插件** 可以直接在编辑器中查询数据库
2. **设置 shell 别名** 简化常用命令：

   ```bash
   alias db-up="docker compose -f docker-compose.dev.yml up -d postgres"
   alias db-down="docker compose -f docker-compose.dev.yml down"
   alias app-start="export \$(cat .env.dev | grep -v '^#' | xargs) && uv run python main.py"
   alias uv-sync="uv sync"
   alias uv-add="uv add"
   ```

3. **使用 .env.dev** 文件管理本地配置
4. **定期备份开发数据** 使用 `pg_dump` 导出数据

## 📚 相关文档

- [Railway 部署指南](./RAILWAY_DEPLOYMENT.md)
- [API 接口文档](http://localhost:8000/docs)
- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
