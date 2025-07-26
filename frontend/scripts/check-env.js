#!/usr/bin/env node

/**
 * 环境配置检查脚本
 * 用于验证 Vercel 部署时的环境变量配置
 */

console.log('🔍 检查环境配置...\n')

// 检查 Node.js 版本
console.log(`📦 Node.js 版本: ${process.version}`)

// 检查环境变量
const envVars = {
  'VITE_API_URL': process.env.VITE_API_URL,
  'VITE_APP_TITLE': process.env.VITE_APP_TITLE,
  'VITE_APP_VERSION': process.env.VITE_APP_VERSION,
  'NODE_ENV': process.env.NODE_ENV,
}

console.log('\n🌍 环境变量:')
Object.entries(envVars).forEach(([key, value]) => {
  if (value) {
    console.log(`  ✅ ${key}: ${value}`)
  } else {
    console.log(`  ⚠️  ${key}: 未设置`)
  }
})

// 检查必需的环境变量
const requiredVars = ['VITE_API_URL']
const missingVars = requiredVars.filter(varName => !process.env[varName])

if (missingVars.length > 0) {
  console.log('\n❌ 缺少必需的环境变量:')
  missingVars.forEach(varName => {
    console.log(`  - ${varName}`)
  })
  console.log('\n💡 请在 Vercel Dashboard 中设置这些环境变量')
  process.exit(1)
} else {
  console.log('\n✅ 所有必需的环境变量都已配置')
}

// 检查 API URL 格式
if (process.env.VITE_API_URL) {
  const apiUrl = process.env.VITE_API_URL
  if (!apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
    console.log('\n⚠️  警告: API URL 应该以 http:// 或 https:// 开头')
  }
  
  if (apiUrl.endsWith('/')) {
    console.log('\n⚠️  警告: API URL 不应该以 / 结尾')
  }
}

console.log('\n🎉 环境配置检查完成!') 