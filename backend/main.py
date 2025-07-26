#!/usr/bin/env python3
"""
Grand Things Backend Server
大事记应用后端服务器启动脚本
"""

import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    # 获取端口，Railway 会设置 PORT 环境变量
    port = int(os.getenv("PORT", 8000))

    # 检查是否在生产环境
    is_production = os.getenv("RAILWAY_ENVIRONMENT") == "production"

    print("🚀 启动 Grand Things API 服务器...")
    print("📝 大事记应用 - 现代化的事件管理平台")
    print(f"🌐 端口: {port}")
    print(f"🔧 环境: {'生产环境' if is_production else '开发环境'}")

    if not is_production:
        print(f"📖 API文档: http://localhost:{port}/docs")
        print(f"💡 健康检查: http://localhost:{port}/health")

    print("=" * 50)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production,  # 生产环境不启用热重载
        log_level="info",
    )
