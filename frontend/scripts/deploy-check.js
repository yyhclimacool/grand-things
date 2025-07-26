#!/usr/bin/env node

/**
 * Vercel 部署前检查脚本
 * 验证配置和环境是否正确
 */

import { existsSync, readFileSync } from 'fs'
import { dirname, join } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const projectRoot = join(__dirname, '..')

console.log('🔍 Vercel 部署前检查...\n')

// 检查必需文件
const requiredFiles = [
  'vercel.json',
  'package.json',
  'vite.config.js',
  'src/config/api.js',
  'vercel-env.example'
]

console.log('📁 检查必需文件:')
let missingFiles = []

requiredFiles.forEach(file => {
  const filePath = join(projectRoot, file)
  if (existsSync(filePath)) {
    console.log(`  ✅ ${file}`)
  } else {
    console.log(`  ❌ ${file} - 缺失`)
    missingFiles.push(file)
  }
})

if (missingFiles.length > 0) {
  console.log('\n❌ 以下文件缺失，请创建后再部署:')
  missingFiles.forEach(file => console.log(`   - ${file}`))
  process.exit(1)
}

// 检查 package.json 中的脚本
console.log('\n📦 检查构建脚本:')
const packageJson = JSON.parse(readFileSync(join(projectRoot, 'package.json'), 'utf8'))

const requiredScripts = ['build', 'vercel-build']
requiredScripts.forEach(script => {
  if (packageJson.scripts[script]) {
    console.log(`  ✅ ${script}: ${packageJson.scripts[script]}`)
  } else {
    console.log(`  ❌ ${script} - 缺失`)
  }
})

// 检查 vercel.json 配置
console.log('\n⚙️ 检查 Vercel 配置:')
const vercelConfig = JSON.parse(readFileSync(join(projectRoot, 'vercel.json'), 'utf8'))

if (vercelConfig.builds?.[0]?.config?.distDir === 'dist') {
  console.log('  ✅ 输出目录: dist')
} else {
  console.log('  ⚠️  输出目录配置可能有问题')
}

if (vercelConfig.routes?.some(route => route.dest === '/index.html')) {
  console.log('  ✅ SPA 路由重写配置正确')
} else {
  console.log('  ⚠️  SPA 路由重写配置可能有问题')
}

// 检查环境变量配置
console.log('\n🌍 环境变量配置提醒:')
console.log('  📝 在 Vercel Dashboard 中设置以下环境变量:')
console.log('     VITE_API_URL=https://grand-things-production.up.railway.app')
console.log('     VITE_APP_TITLE=Grand Things - 大事记')
console.log('     VITE_APP_VERSION=1.0.0')

// 检查 API 配置
console.log('\n🔗 API 配置检查:')
try {
  const apiConfigPath = join(projectRoot, 'src/config/api.js')
  const apiConfig = readFileSync(apiConfigPath, 'utf8')
  
  if (apiConfig.includes('import.meta.env.VITE_API_URL')) {
    console.log('  ✅ API 配置支持环境变量')
  } else {
    console.log('  ⚠️  API 配置可能不支持环境变量')
  }
} catch (error) {
  console.log('  ❌ 无法读取 API 配置文件')
}

console.log('\n🎯 部署建议:')
console.log('  1. 确保后端 Railway 应用正常运行')
console.log('  2. 在 Vercel Dashboard 中设置环境变量')
console.log('  3. 推送代码到 GitHub')
console.log('  4. 连接 Vercel 到 GitHub 仓库')
console.log('  5. 设置 Root Directory 为 "frontend"')

console.log('\n✅ 检查完成！准备部署到 Vercel 🚀') 