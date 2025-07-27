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
import os


def get_database_url():
    """获取数据库连接URL，支持开发和生产环境"""
    # 优先使用环境变量中的DATABASE_URL
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        print(f"🔧 使用环境变量DATABASE_URL: {database_url}")
        return database_url

    # 开发环境默认配置
    dev_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "grand_things"),
        "username": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres"),
    }

    dev_url = f"postgresql://{dev_config['username']}:{dev_config['password']}@{dev_config['host']}:{dev_config['port']}/{dev_config['database']}"
    print(f"🔧 使用开发环境配置: {dev_url}")
    return dev_url


# 获取数据库连接URL
DATABASE_URL = get_database_url()


def create_engine_with_config():
    """创建数据库引擎，适配不同环境"""

    # 基础引擎配置
    engine_kwargs = {
        "echo": False,  # 生产环境不打印SQL
        "pool_pre_ping": True,  # 连接池健康检查
        "pool_recycle": 3600,  # 1小时后回收连接
    }

    # 开发环境配置
    if os.getenv("RAILWAY_ENVIRONMENT") != "production":
        engine_kwargs.update(
            {
                "echo": False,  # 可以设为True查看SQL调试
                "pool_size": 5,
                "max_overflow": 10,
            }
        )
        print("🏗️  配置开发环境数据库引擎")
    else:
        # 生产环境配置
        engine_kwargs.update(
            {
                "pool_size": 20,
                "max_overflow": 30,
                "pool_timeout": 30,
            }
        )
        print("🏗️  配置生产环境数据库引擎")

    try:
        engine = create_engine(DATABASE_URL, **engine_kwargs)

        # 测试连接
        with engine.connect() as conn:
            from sqlalchemy import text

            result = conn.execute(text("SELECT 1")).scalar()
            if result == 1:
                print("✅ 数据库连接测试成功")
            else:
                print("⚠️  数据库连接测试异常")

        return engine

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print(f"📍 DATABASE_URL: {DATABASE_URL}")
        raise


# 创建数据库引擎
engine = create_engine_with_config()

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
    """创建数据库表结构"""
    print("🏗️  开始创建数据库表...")
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")

        # 验证表是否正确创建
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if tables:
            print(f"📋 已创建的数据表: {', '.join(tables)}")
            for table_name in tables:
                columns = inspector.get_columns(table_name)
                print(f"  📊 {table_name}: {len(columns)} 个字段")
        else:
            print("⚠️  警告: 没有检测到任何数据表")

    except Exception as e:
        print(f"❌ 数据库表创建失败: {e}")
        print(f"📍 数据库URL: {DATABASE_URL}")
        raise


# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
