#!/usr/bin/env python3
"""
数据库初始化脚本
支持 PostgreSQL 数据库的初始化和表创建
"""

import os
import sys
from app.database import create_tables, DATABASE_URL, engine


def test_database_connection():
    """测试数据库连接"""
    print("🔗 测试数据库连接...")

    try:
        # 测试基本连接
        with engine.connect() as conn:
            from sqlalchemy import text

            result = conn.execute(text("SELECT version()")).scalar()
            print(f"✅ 数据库连接成功")
            print(f"📊 PostgreSQL 版本: {result}")
            return True

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print(f"📍 数据库URL: {DATABASE_URL}")

        # 提供连接问题的诊断信息
        if "could not connect to server" in str(e).lower():
            print("💡 可能的解决方案:")
            print("   - 检查 PostgreSQL 服务是否启动")
            print("   - 检查数据库URL配置是否正确")
            print("   - 检查网络连接")
            if "localhost" in DATABASE_URL:
                print(
                    "   - 本地开发：运行 docker-compose -f docker-compose.dev.yml up -d"
                )
        elif "authentication failed" in str(e).lower():
            print("💡 可能的解决方案:")
            print("   - 检查数据库用户名和密码")
            print("   - 检查数据库用户权限")
        elif "database" in str(e).lower() and "does not exist" in str(e).lower():
            print("💡 可能的解决方案:")
            print("   - 检查数据库名称是否正确")
            print("   - 确认目标数据库已创建")

        return False


def init_database():
    """初始化数据库"""
    print("🚀 开始 PostgreSQL 数据库初始化...")
    print(f"📍 数据库URL: {DATABASE_URL}")

    # 检测数据库类型
    if DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith(
        "postgres://"
    ):
        print("🐘 检测到 PostgreSQL 数据库")
    else:
        print(f"⚠️  未知的数据库类型: {DATABASE_URL}")
        return False

    # 测试数据库连接
    if not test_database_connection():
        return False

    # 创建数据库表
    try:
        print("🏗️  开始创建数据库表结构...")
        create_tables()
        print("✅ 数据库初始化成功")
        return True

    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")

        # 提供表创建问题的诊断信息
        if "permission denied" in str(e).lower():
            print("💡 可能的解决方案:")
            print("   - 检查数据库用户是否有CREATE权限")
            print("   - 检查数据库连接用户的权限设置")
        elif "already exists" in str(e).lower():
            print("💡 表可能已经存在，这通常不是问题")
            print("   - 可以忽略此错误或删除现有表后重试")

        return False


if __name__ == "__main__":
    success = init_database()
    if not success:
        print("💥 数据库初始化失败，退出程序")
        sys.exit(1)
    else:
        print("🎉 PostgreSQL 数据库初始化完成")
