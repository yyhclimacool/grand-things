#!/bin/bash

set -e

echo "🚀 开始部署 Grand Things 大事记应用"
echo "====================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：未找到Docker，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误：未找到docker-compose，请先安装docker-compose"
    exit 1
fi

echo "✅ Docker环境检查通过"

# 创建必要的目录
echo "📁 创建数据目录..."
mkdir -p data logs

# 停止现有容器（如果存在）
echo "🛑 停止现有服务..."
docker-compose down || true

# 构建并启动服务
echo "🔨 构建Docker镜像..."
docker-compose build --no-cache

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 健康检查
echo "🏥 进行健康检查..."
for i in {1..30}; do
    if curl -s http://localhost/health > /dev/null; then
        echo "✅ 服务启动成功！"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "❌ 服务启动失败，请检查日志"
        docker-compose logs
        exit 1
    fi
    
    echo "⏳ 等待中... ($i/30)"
    sleep 2
done

echo ""
echo "🎉 Grand Things 部署成功！"
echo "====================================="
echo "🌐 访问地址: http://localhost"
echo "📚 API文档: http://localhost/docs"
echo "💡 健康检查: http://localhost/health"
echo ""
echo "📊 查看运行状态: docker-compose ps"
echo "📝 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"
echo "=====================================" 