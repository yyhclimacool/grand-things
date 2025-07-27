#!/bin/bash

# Grand Things 本地开发环境启动脚本

set -e

echo "🚀 Grand Things 本地开发环境启动"
echo "================================="

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 检查 docker compose 是否可用
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装或不可用"
    exit 1
fi

# 进入后端目录
cd backend

echo "📦 检查环境变量文件..."
if [ ! -f ".env.dev" ]; then
    if [ -f "env.dev.example" ]; then
        echo "📋 复制环境变量示例文件..."
        cp env.dev.example .env.dev
        echo "✅ 已创建 .env.dev 文件，请根据需要修改配置"
    else
        echo "❌ 找不到环境变量示例文件"
        exit 1
    fi
else
    echo "✅ 环境变量文件已存在"
fi

echo "🐘 启动 PostgreSQL 数据库..."
cd ..
docker compose -f docker-compose.dev.yml up -d postgres

echo "⏳ 等待数据库启动..."
sleep 5

# 检查数据库是否准备就绪
echo "🔍 检查数据库连接..."
until docker exec grand-things-postgres pg_isready -U postgres -d grand_things; do
    echo "   数据库未就绪，继续等待..."
    sleep 2
done

echo "✅ 数据库已就绪"

cd backend

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安装，请先安装 uv:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   或访问: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

echo "📦 使用 uv 同步依赖..."
uv sync

echo "🗄️  初始化数据库..."
uv run python init_db.py

if [ $? -eq 0 ]; then
    echo "✅ 数据库初始化成功"
else
    echo "❌ 数据库初始化失败"
    exit 1
fi

echo ""
echo "🎉 开发环境启动完成！"
echo ""
echo "📱 服务地址："
echo "   应用API:    http://localhost:8000"
echo "   API文档:    http://localhost:8000/docs"
echo "   健康检查:   http://localhost:8000/health"
echo "   pgAdmin:    http://localhost:8080"
echo ""
echo "🗄️  数据库信息："
echo "   主机: localhost:5432"
echo "   数据库: grand_things"
echo "   用户名: postgres"
echo "   密码: postgres"
echo ""
echo "🔧 常用命令："
echo "   启动应用: export \$(cat .env.dev | grep -v '^#' | xargs) && uv run python main.py"
echo "   运行脚本: uv run <script_name>"
echo "   安装依赖: uv sync"
echo "   添加依赖: uv add <package_name>"
echo "   停止数据库: docker compose -f ../docker-compose.dev.yml down"
echo "   查看日志: docker compose -f ../docker-compose.dev.yml logs postgres"
echo ""

# 询问是否立即启动应用
read -p "💫 是否现在启动应用服务器? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 启动应用服务器..."
    export $(cat .env.dev | grep -v '^#' | xargs)
    uv run python main.py
else
    echo "👋 开发环境已准备就绪，可以手动启动应用"
fi 