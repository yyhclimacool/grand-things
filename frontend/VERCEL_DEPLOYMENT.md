# 🚀 Grand Things 前端 - Vercel 部署指南

完整的前端部署指南，连接到你的 Railway 后端。

## 📋 前端部署配置清单

### ✅ **已完成的配置**
- ✅ `vercel.json` - Vercel 部署配置
- ✅ `src/config/api.js` - 统一 API 配置，支持环境变量
- ✅ `vite.config.js` - 优化的构建配置
- ✅ `.vercelignore` - 忽略不必要文件
- ✅ `scripts/check-env.js` - 环境变量检查
- ✅ `scripts/deploy-check.js` - 部署前检查
- ✅ `vercel-env.example` - Vercel 环境变量示例

## 🚀 立即部署步骤

### **第一步：部署前检查**
```bash
cd frontend
npm run deploy-check
```

### **第二步：推送代码到 GitHub**
```bash
# 在项目根目录
git add .
git commit -m "前端适配 Vercel 部署"
git push origin main
```

### **第三步：连接 Vercel**

1. **访问 Vercel**
   - 打开 [vercel.com](https://vercel.com)
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择你的 `grand-things` 仓库

3. **配置项目设置**
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend` ⚠️ **重要**
   - **Build Command**: `npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `npm ci`

### **第四步：设置环境变量**

在 Vercel Dashboard 中设置：

```bash
# 必需的环境变量
VITE_API_URL=https://grand-things-production.up.railway.app

# 可选的环境变量
VITE_APP_TITLE=Grand Things - 大事记
VITE_APP_VERSION=1.0.0
VITE_APP_DESCRIPTION=现代化的个人大事记管理应用
```

### **第五步：部署完成**

部署成功后，你会得到类似的 URL：
```
https://grand-things-你的用户名.vercel.app
```

## 🔧 **项目结构说明**

```
frontend/                    # Vercel 部署的根目录
├── vercel.json             # Vercel 配置文件
├── vercel-env.example      # 环境变量示例
├── .vercelignore           # 忽略文件配置
├── package.json            # 包含 vercel-build 脚本
├── vite.config.js          # 优化的构建配置
├── src/
│   └── config/
│       └── api.js          # 统一 API 配置
└── scripts/
    ├── check-env.js        # 环境检查脚本
    └── deploy-check.js     # 部署前检查脚本
```

## 📊 **重要配置文件详解**

### **1. vercel.json - Vercel 部署配置**
```json
{
  "version": 2,
  "name": "grand-things-frontend",
  "builds": [{
    "src": "package.json",
    "use": "@vercel/static-build",
    "config": { "distDir": "dist" }
  }],
  "routes": [
    { "handle": "filesystem" },
    { "src": "/(.*)", "dest": "/index.html" }  // SPA 路由重写
  ]
}
```

### **2. src/config/api.js - API 配置**
```javascript
const getApiBaseUrl = () => {
  // Vercel 部署时使用环境变量
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  // 开发环境
  if (import.meta.env.DEV) {
    return 'http://localhost:8000'
  }
  // 生产环境默认
  return '/api'
}
```

### **3. package.json - 构建脚本**
```json
{
  "scripts": {
    "build": "vite build",
    "vercel-build": "vite build",      // Vercel 构建命令
    "deploy-check": "node scripts/deploy-check.js",
    "pre-deploy": "npm run deploy-check && npm run build"
  }
}
```

## 🌍 **环境配置说明**

### **开发环境**
```bash
# 本地开发
VITE_API_URL=http://localhost:8000
```

### **生产环境 (Vercel)**
```bash
# 连接到 Railway 后端
VITE_API_URL=https://grand-things-production.up.railway.app
```

## 🔗 **前后端连接配置**

### **前端 → 后端**
- **Vercel 环境变量**: `VITE_API_URL=https://grand-things-production.up.railway.app`

### **后端 → 前端**
- **Railway 环境变量**: `ALLOWED_ORIGINS=https://your-app.vercel.app`

## 🛠️ **本地测试命令**

```bash
# 环境检查
npm run check-env

# 部署前检查
npm run deploy-check

# 构建测试
npm run build

# 预览构建结果
npm run preview

# 完整部署准备
npm run pre-deploy
```

## 🚨 **常见问题解决**

### **1. API 连接失败**
```bash
# 检查环境变量
console.log('API Base URL:', import.meta.env.VITE_API_URL)

# 确认 Railway 后端正常
curl https://grand-things-production.up.railway.app/health
```

### **2. 路由 404 错误**
```bash
# 确认 vercel.json 中有 SPA 路由重写
{ "src": "/(.*)", "dest": "/index.html" }
```

### **3. 构建失败**
```bash
# 检查 Node.js 版本兼容性
# 查看 Vercel 构建日志
# 确认所有依赖都在 package.json 中
```

### **4. CORS 错误**
```bash
# 确认 Railway 后端设置了正确的 ALLOWED_ORIGINS
# 检查前端的 API URL 是否正确
```

## 📈 **性能优化**

### **已配置的优化**
- ✅ **代码分割** - vendor、element-plus、utils 分包
- ✅ **静态资源缓存** - 1年缓存策略
- ✅ **安全头** - XSS 保护、内容类型检测
- ✅ **现代构建目标** - ESNext，更小的包体积

### **构建优化配置**
```javascript
// vite.config.js
export default defineConfig({
  build: {
    target: 'esnext',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          elementui: ['element-plus'],
          utils: ['axios', 'dayjs']
        }
      }
    }
  }
})
```

## 🎯 **部署后验证**

### **1. 功能测试**
- ✅ 网站正常加载
- ✅ 路由导航正常
- ✅ 主题切换功能
- ✅ API 请求正常

### **2. 性能测试**
- 访问 [PageSpeed Insights](https://pagespeed.web.dev/)
- 输入你的 Vercel URL 测试性能

### **3. 连接测试**
```bash
# 浏览器开发者工具 Network 标签
# 确认 API 请求指向正确的 Railway 地址
# 检查是否有 CORS 错误
```

## 🔄 **自动部署流程**

配置完成后，每次推送代码都会自动部署：

```bash
git add .
git commit -m "更新前端功能"
git push origin main
# → Vercel 自动检测更改并重新部署
```

## 📝 **部署完成检查清单**

- [ ] **Vercel 项目创建成功**
- [ ] **Root Directory 设置为 `frontend`**
- [ ] **环境变量 `VITE_API_URL` 已设置**
- [ ] **构建成功，无错误**
- [ ] **网站可以正常访问**
- [ ] **API 连接正常**
- [ ] **所有页面路由正常**
- [ ] **主题切换正常**
- [ ] **Railway 后端 CORS 已配置**

---

**🎊 恭喜！你的 Grand Things 前端已成功部署到 Vercel！**

**访问地址**：`https://your-app.vercel.app`
**后端地址**：`https://grand-things-production.up.railway.app` 