# 🚀 Grand Things 前端 - Vercel 部署指南

这个指南专门介绍如何将 Grand Things 前端部署到 Vercel 平台。

## 📋 准备工作

### 1. 代码调整（已完成）
- ✅ 创建了统一的 API 配置系统
- ✅ 支持环境变量配置 API 地址
- ✅ 优化了构建配置
- ✅ 添加了 Vercel 配置文件

### 2. 后端 API 准备
你需要先部署后端 API，推荐选项：
- **Railway**: https://railway.app (免费额度)
- **Render**: https://render.com (免费额度) 
- **你的 VPS**: 使用 Docker 部署

## 🚀 Vercel 部署步骤

### 方案一：通过 GitHub 自动部署（推荐）

#### 1. 推送代码到 GitHub
```bash
# 如果还没有 Git 仓库
git init
git add .
git commit -m "准备 Vercel 部署"

# 推送到 GitHub
git remote add origin https://github.com/你的用户名/grand-things.git
git push -u origin main
```

#### 2. 连接 Vercel
1. 访问 [vercel.com](https://vercel.com)
2. 使用 GitHub 账号登录
3. 点击 "New Project"
4. 选择你的 `grand-things` 仓库
5. 配置项目设置：

**构建设置**：
- Framework Preset: `Vite`
- Root Directory: `frontend` 
- Build Command: `npm run build`
- Output Directory: `frontend/dist`

#### 3. 配置环境变量
在 Vercel Dashboard 中设置环境变量：

```
VITE_API_URL=https://your-backend-api-url.com
VITE_APP_TITLE=Grand Things - 大事记
VITE_APP_VERSION=1.0.0
```

#### 4. 部署
点击 "Deploy" 按钮，等待构建完成。

### 方案二：使用 Vercel CLI

#### 1. 安装 Vercel CLI
```bash
npm i -g vercel
```

#### 2. 登录并部署
```bash
cd frontend

# 登录 Vercel
vercel login

# 部署
vercel --prod
```

#### 3. 配置环境变量
```bash
# 设置 API URL
vercel env add VITE_API_URL

# 设置应用信息
vercel env add VITE_APP_TITLE
vercel env add VITE_APP_VERSION
```

## 🔧 环境变量配置

### 必需的环境变量
| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `VITE_API_URL` | 后端 API 地址 | `https://your-api.railway.app` |
| `VITE_APP_TITLE` | 应用标题 | `Grand Things - 大事记` |
| `VITE_APP_VERSION` | 版本号 | `1.0.0` |

### 后端 API 地址配置

#### 如果后端部署在 Railway：
```
VITE_API_URL=https://your-app-name.up.railway.app
```

#### 如果后端部署在 Render：
```
VITE_API_URL=https://your-app-name.onrender.com
```

#### 如果后端部署在你的 VPS：
```
VITE_API_URL=https://your-domain.com/api
```

## 🎯 部署后检查

### 1. 功能测试
- ✅ 网站可以正常访问
- ✅ 主题切换功能正常
- ✅ 路由导航正常
- ✅ API 请求正常（需要后端配合）

### 2. 性能检查
访问 [PageSpeed Insights](https://pagespeed.web.dev/) 测试你的网站性能。

### 3. 查看构建日志
在 Vercel Dashboard 的 "Deployments" 页面可以查看构建日志。

## 🔄 自动部署

配置完成后，每次推送到 GitHub 主分支都会自动触发 Vercel 部署。

### 分支部署策略
- `main` 分支 → 生产环境
- 其他分支 → 预览环境

## 📊 监控和分析

### Vercel Analytics
在项目设置中启用 Vercel Analytics 来监控：
- 页面访问量
- 性能指标
- 用户行为

### Real-time Functions
如果需要实时功能，可以考虑使用 Vercel Functions。

## 🚨 常见问题

### 1. API 跨域问题
**问题**：前端无法访问后端 API
**解决**：确保后端配置了正确的 CORS 设置：

```python
# FastAPI 后端
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-domain.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 环境变量不生效
**问题**：配置的环境变量在应用中获取不到
**解决**：
1. 确保变量名以 `VITE_` 开头
2. 在 Vercel Dashboard 中重新部署
3. 检查变量名拼写

### 3. 构建失败
**问题**：Vercel 构建过程出错
**解决**：
1. 检查 `package.json` 中的依赖版本
2. 查看构建日志中的错误信息
3. 本地运行 `npm run build` 测试

### 4. 路由 404 错误
**问题**：直接访问路由返回 404
**解决**：已在 `vercel.json` 中配置了 SPA 路由重写，应该正常工作。

## 🔧 本地测试生产构建

在部署前，建议本地测试生产构建：

```bash
cd frontend

# 设置生产环境变量
export VITE_API_URL=https://your-backend-url.com

# 构建
npm run build

# 预览构建结果
npm run preview
```

## 📝 更新应用

### 1. 代码更新
```bash
git add .
git commit -m "更新功能"
git push origin main
```

### 2. 环境变量更新
在 Vercel Dashboard 中修改环境变量后，需要重新部署。

## 🎉 部署完成

部署成功后，你的应用将可以通过类似这样的地址访问：
`https://grand-things-你的用户名.vercel.app`

你也可以在 Vercel Dashboard 中配置自定义域名。

## 💡 下一步

1. 配置自定义域名
2. 设置性能监控
3. 配置 CDN 加速
4. 添加错误监控（如 Sentry）

---

**恭喜！你的 Grand Things 前端已经成功部署到 Vercel！** 🎉 