#!/usr/bin/env python3
"""
环境检查脚本
验证开发环境是否正确配置
"""

import sys
import os
import subprocess
from pathlib import Path


def check_uv():
    """检查 uv 是否安装"""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv 已安装: {result.stdout.strip()}")
            return True
        else:
            print("❌ uv 未正确安装")
            return False
    except FileNotFoundError:
        print("❌ uv 未安装")
        print("💡 安装方法:")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False


def check_pyproject():
    """检查 pyproject.toml 文件"""
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        print("✅ pyproject.toml 文件存在")
        return True
    else:
        print("❌ pyproject.toml 文件不存在")
        return False


def check_uv_env():
    """检查 uv 虚拟环境"""
    try:
        result = subprocess.run(["uv", "pip", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ uv 虚拟环境可用")
            return True
        else:
            print("⚠️  uv 虚拟环境未初始化，运行 'uv sync' 来创建")
            return False
    except Exception as e:
        print(f"❌ 检查 uv 环境时出错: {e}")
        return False


def check_dependencies():
    """检查关键依赖"""
    key_packages = ["fastapi", "sqlalchemy", "psycopg2-binary"]

    try:
        result = subprocess.run(["uv", "pip", "list"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ 无法获取依赖列表")
            return False

        installed_packages = result.stdout.lower()
        missing_packages = []

        for package in key_packages:
            if package.lower() not in installed_packages:
                missing_packages.append(package)

        if not missing_packages:
            print("✅ 关键依赖已安装")
            return True
        else:
            print(f"⚠️  缺少依赖: {', '.join(missing_packages)}")
            print("   运行 'uv sync' 来安装依赖")
            return False

    except Exception as e:
        print(f"❌ 检查依赖时出错: {e}")
        return False


def check_env_file():
    """检查环境变量文件"""
    env_files = [".env.dev", "env.dev.example"]

    for env_file in env_files:
        if Path(env_file).exists():
            print(f"✅ 找到环境文件: {env_file}")
            if env_file == ".env.dev":
                return True

    print("⚠️  未找到 .env.dev 文件")
    print("   复制 env.dev.example 为 .env.dev 并配置")
    return False


def check_database_connection():
    """检查数据库连接（可选）"""
    try:
        from app.database import engine

        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT 1")).scalar()
            if result == 1:
                print("✅ 数据库连接正常")
                return True
            else:
                print("❌ 数据库连接异常")
                return False

    except ImportError:
        print("⚠️  无法导入数据库模块，请确保依赖已安装")
        return False
    except Exception as e:
        print(f"⚠️  数据库连接测试失败: {e}")
        print("   可能是数据库未启动或配置不正确")
        return False


def main():
    """主检查函数"""
    print("🔍 Grand Things 开发环境检查")
    print("=" * 40)

    checks = [
        ("uv 安装", check_uv),
        ("pyproject.toml", check_pyproject),
        ("uv 虚拟环境", check_uv_env),
        ("关键依赖", check_dependencies),
        ("环境变量文件", check_env_file),
        ("数据库连接", check_database_connection),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n📋 检查 {name}...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 检查 {name} 时出错: {e}")
            results.append((name, False))

    print("\n" + "=" * 40)
    print("📊 检查结果汇总:")

    passed = 0
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {name}")
        if result:
            passed += 1

    print(f"\n通过: {passed}/{len(results)}")

    if passed == len(results):
        print("\n🎉 环境配置完美！可以开始开发了")
    elif passed >= len(results) - 1:  # 允许数据库连接失败
        print("\n✨ 环境基本就绪，请检查失败的项目")
    else:
        print("\n⚠️  请修复环境问题后重试")
        print("\n💡 常用修复命令:")
        print("   uv sync          # 同步依赖")
        print("   cp env.dev.example .env.dev  # 复制环境文件")
        print(
            "   docker compose -f ../docker-compose.dev.yml up -d postgres  # 启动数据库"
        )


if __name__ == "__main__":
    main()
