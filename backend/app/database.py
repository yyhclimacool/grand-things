from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import sqlite3
import os

# 数据库文件路径 - 支持环境变量
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./grand_things.db")

print(f"🔧 数据库URL配置: {DATABASE_URL}")

# 确保数据目录存在
if DATABASE_URL.startswith("sqlite:///"):
    # 正确解析数据库路径
    db_path = DATABASE_URL.replace("sqlite:///", "")

    # 如果路径不是绝对路径，转为绝对路径
    if not os.path.isabs(db_path):
        db_path = os.path.abspath(db_path)

    print(f"📍 数据库文件路径: {db_path}")

    # 获取数据库目录
    db_dir = os.path.dirname(db_path)
    print(f"📁 数据库目录: {db_dir}")

    # 检查目录是否存在
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
            print(f"✅ 成功创建数据库目录: {db_dir}")
        except Exception as e:
            print(f"❌ 创建数据库目录失败: {e}")
    else:
        print(f"📂 数据库目录已存在: {db_dir}")

    # 检查目录权限
    if os.path.exists(db_dir):
        is_writable = os.access(db_dir, os.W_OK)
        print(f"✏️  目录可写权限: {is_writable}")

        # 列出目录内容
        try:
            files = os.listdir(db_dir)
            print(f"📋 目录内容: {files}")
        except Exception as e:
            print(f"❌ 无法列出目录内容: {e}")

    # 检查数据库文件是否存在
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        print(f"📊 数据库文件已存在，大小: {file_size} bytes")
    else:
        print(f"🆕 数据库文件不存在，将创建新文件: {db_path}")

# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


# 用户模型
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系：用户拥有的事件
    events = relationship("Event", back_populates="user")


# 事件模型
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    event_date = Column(DateTime, default=datetime.utcnow)
    tags = Column(String(500))  # 存储为逗号分隔的字符串
    category = Column(String(50))
    impact_score = Column(Integer, default=0)  # 影响评分 0-10
    feedback = Column(Text)  # 后续反馈
    is_reviewed = Column(Boolean, default=False)

    # 用户关联（外键）
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True
    )  # 允许为空以兼容现有数据

    # 关系：事件属于的用户
    user = relationship("User", back_populates="events")


# 标签模型
class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default="#3B82F6")  # 十六进制颜色
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


# 创建所有表
def create_tables():
    print("🏗️  开始创建数据库表...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")

        # 验证数据库文件是否正确创建
        if DATABASE_URL.startswith("sqlite:///"):
            db_path = DATABASE_URL.replace("sqlite:///", "")
            if not os.path.isabs(db_path):
                db_path = os.path.abspath(db_path)

            if os.path.exists(db_path):
                file_size = os.path.getsize(db_path)
                print(f"📊 数据库文件创建完成，大小: {file_size} bytes")
            else:
                print(f"⚠️  警告: 数据库文件可能未正确创建: {db_path}")

    except Exception as e:
        print(f"❌ 数据库表创建失败: {e}")
        raise


# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
