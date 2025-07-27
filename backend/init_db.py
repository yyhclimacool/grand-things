#!/usr/bin/env python3
"""
数据库初始化脚本
确保数据库文件正确创建在Volume挂载点
"""

import os
import sys
from app.database import create_tables, DATABASE_URL


def init_database():
    """初始化数据库"""
    print("🚀 开始数据库初始化...")
    print(f"📍 数据库URL: {DATABASE_URL}")

    # 如果是SQLite数据库，确保文件在正确位置
    if DATABASE_URL.startswith("sqlite:///"):
        db_path = DATABASE_URL.replace("sqlite:///", "")

        # 确保使用绝对路径
        if not os.path.isabs(db_path):
            db_path = os.path.abspath(db_path)

        print(f"📊 数据库文件路径: {db_path}")

        # 检查目录
        db_dir = os.path.dirname(db_path)
        print(f"📁 数据库目录: {db_dir}")

        # 特别检查 /app/data 目录
        if db_dir == "/app/data":
            print("🔍 检测到Railway Volume目录 /app/data")

            if not os.path.exists(db_dir):
                print(f"❌ Volume目录不存在: {db_dir}")
                print("⚠️  请确认Railway Volume正确配置并挂载到 /app/data")
                return False
            else:
                print(f"✅ Volume目录存在: {db_dir}")

                # 检查权限
                if not os.access(db_dir, os.W_OK):
                    print(f"❌ Volume目录没有写权限: {db_dir}")
                    return False
                else:
                    print(f"✅ Volume目录有写权限")

    # 创建数据库表
    try:
        create_tables()
        print("✅ 数据库初始化成功")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    if not success:
        print("💥 数据库初始化失败，退出程序")
        sys.exit(1)
    else:
        print("🎉 数据库初始化完成")
