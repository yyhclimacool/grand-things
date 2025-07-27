# 🚂 Railway 后端部署指南

本指南介绍如何将 Grand Things 后端部署到 Railway 平台。

## 📋 准备工作

### ✅ **已完成的代码调整**
- ✅ 主启动文件适配 Railway 端口配置
- ✅ CORS 配置支持生产环境动态域名
- ✅ 健康检查端点配置
- ✅ Railway 配置文件 `railway.toml`
- ✅ 环境变量示例文件

## 🚀 部署步骤

### **第一步：推送代码到 GitHub**
```bash
git add .
git commit -m "适配 Railway 部署"
git push origin main
```

### **第二步：在 Railway 创建项目**

1. **访问 Railway**
   - 打开 [railway.app](https://railway.app)
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的 `grand-things` 仓库

3. **配置项目设置**
   - 在部署配置中设置 **Root Directory** 为 `backend`
   - Railway 会自动检测到 Python 项目
   - 自动读取 `backend/railway.toml` 配置
   - 使用 uv 自动安装 `pyproject.toml` 中的依赖

### **第三步：添加 PostgreSQL 数据库**

1. **添加 PostgreSQL 插件**
   - 在项目页面点击 "New Service" 
   - 选择 "Database" → "Add PostgreSQL"
   - PostgreSQL 数据库将自动创建并连接到你的项目
   - `DATABASE_URL` 环境变量会自动设置

### **第四步：配置环境变量**

在 Railway Dashboard 中设置以下环境变量：

#### **必需的环境变量**
```bash
# 跨域配置（最重要）
ALLOWED_ORIGINS=https://your-frontend.vercel.app

# JWT 密钥（生产环境）
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-too
```

#### **可选的环境变量**
```bash
# JWT 配置
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
DEBUG=false

# 注意：DATABASE_URL 由 PostgreSQL 插件自动提供，无需手动设置
```

### **第五步：部署完成**

1. **获取 Railway URL**
   - 部署完成后，Railway 会提供一个类似这样的 URL：
   ```
   https://your-app-name.up.railway.app
   ```

2. **测试部署**
   - 访问 `https://your-app.railway.app/health` 检查健康状态
   - 访问 `https://your-app.railway.app/docs` 查看 API 文档
   - 检查数据库连接：应用启动日志会显示 PostgreSQL 连接状态

## 🔧 **Railway 自动处理的配置**

Railway 会自动设置以下环境变量：
- `PORT` - 应用监听端口
- `RAILWAY_ENVIRONMENT=production` - 生产环境标识

## 📊 **部署配置说明**

### **backend/railway.toml 配置解释**
```toml
[build]
builder = "NIXPACKS"          # 使用 Nixpacks 构建器

[deploy]
# PostgreSQL 版本配置（使用 uv）
startCommand = "uv sync && uv run python init_db.py && uv run python main.py"  # 同步依赖、初始化数据库、启动应用
healthcheckPath = "/health"    # 健康检查路径
healthcheckTimeout = 300       # 健康检查超时时间（延长以适应数据库初始化）
restartPolicyType = "ON_FAILURE"  # 重启策略

[env]
# DATABASE_URL 会由 PostgreSQL 插件自动提供
```

**注意**：
- 配置文件位于 `backend/railway.toml`，Railway 部署时需要设置 **Root Directory** 为 `backend`
- 应用启动前会自动运行数据库初始化脚本
- PostgreSQL 连接URL由Railway自动管理

### **代码调整说明**

#### 1. **端口配置**
```python
# 主启动文件自动读取 Railway 的 PORT 环境变量
port = int(os.getenv("PORT", 8000))
```

#### 2. **CORS 配置**
```python
# 支持从环境变量读取允许的域名
def get_allowed_origins():
    origins = ["http://localhost:3000", "http://localhost:5173"]  # 开发环境
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
    if allowed_origins:
        origins.extend([origin.strip() for origin in allowed_origins.split(",")])
    return origins
```

#### 3. **生产环境优化**
```python
# 生产环境不启用热重载
is_production = os.getenv("RAILWAY_ENVIRONMENT") == "production"
uvicorn.run("app.main:app", reload=not is_production)
```

## 🔄 **自动部署流程**

配置完成后，每次推送代码到 GitHub 都会自动触发 Railway 部署：

```bash
git add .
git commit -m "更新后端功能"
git push origin main
# → Railway 自动检测到更改并重新部署
```

## 🌐 **连接前端**

部署完成后，你需要在前端配置中设置 Railway 的 URL：

**Vercel 环境变量**：
```bash
VITE_API_URL=https://your-app.railway.app
```

**同时在 Railway 中设置**：
```bash
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

## 📈 **监控和日志**

### **Railway Dashboard 功能**
- 📊 **实时监控** - CPU、内存、网络使用情况
- 📝 **日志查看** - 实时查看应用日志
- 🔄 **部署历史** - 查看和回滚部署
- ⚡ **性能指标** - 响应时间、错误率

### **健康检查**
Railway 会定期访问 `/health` 端点检查应用状态：
```python
@app.get("/health")
async def health():
    return {"status": "healthy", "message": "大事记应用运行正常"}
```

## 🚨 **常见问题**

### **1. 部署失败**
```bash
# 检查 requirements.txt 是否完整
# 查看 Railway 部署日志
# 确认 railway.toml 配置正确
```

### **2. CORS 错误**
```bash
# 确保在 Railway 中设置了 ALLOWED_ORIGINS
# 检查域名是否完全匹配（包括 https://）
# 确认没有多余的斜杠
```

### **3. 健康检查失败**
```bash
# 确认 /health 端点可以访问
# 检查应用是否在指定端口启动
# 查看应用日志排查错误
```

### **4. 数据库连接问题**
```bash
# 检查 PostgreSQL 插件是否正确添加
# 确认 DATABASE_URL 环境变量已自动设置
# 查看应用启动日志中的数据库连接状态
# 如果连接失败，检查数据库服务是否正常运行
```

## 💡 **最佳实践**

### **1. 安全配置**
- 使用强密码作为 `SECRET_KEY` 和 `JWT_SECRET_KEY`
- 定期轮换密钥
- 只允许必要的跨域来源

### **2. 性能优化**
- 生产环境关闭调试模式 (`DEBUG=false`)
- 关闭热重载功能
- 使用适当的日志级别

### **3. 监控运维**
- 定期检查 Railway Dashboard 中的性能指标
- 关注错误日志
- 设置合适的健康检查超时时间

## 🎉 **部署完成检查清单**

- [ ] **代码推送成功** - 最新代码在 GitHub
- [ ] **Railway 部署成功** - 显示 "Active" 状态
- [ ] **环境变量设置** - 所有必需变量已配置
- [ ] **健康检查通过** - `/health` 返回正常状态
- [ ] **API 文档可访问** - `/docs` 页面正常显示
- [ ] **CORS 配置正确** - 前端可以正常调用 API
- [ ] **认证功能正常** - 登录/注册接口工作正常

---

**🎊 恭喜！你的 Grand Things 后端已成功部署到 Railway！**

**下一步**：配置前端连接到这个 Railway URL，完成全栈部署。 