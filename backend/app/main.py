from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import create_tables
from .api import events, auth

# 创建FastAPI应用
app = FastAPI(
    title="Grand Things - 大事记应用",
    description="一个现代化的大事记应用，支持事件管理、自动标签提取、时间线展示等功能",
    version="1.0.0",
)

# 配置CORS - 支持开发和生产环境
import os


def get_allowed_origins():
    """获取允许的跨域来源"""
    # 开发环境的默认地址
    origins = [
        "http://localhost:3000",  # React默认端口
        "http://localhost:5173",  # Vite默认端口
        "http://localhost:55361",  # 本地代理端口
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # 从环境变量获取生产环境的允许来源
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
    if allowed_origins:
        # 支持逗号分隔的多个域名
        origins.extend([origin.strip() for origin in allowed_origins.split(",")])

    print(f"🌐 允许的跨域来源: {origins}")
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)  # 认证路由
app.include_router(events.router)  # 事件路由


# 启动时创建数据库表
@app.on_event("startup")
async def startup_event():
    create_tables()


# 根路径
@app.get("/")
async def root():
    return {"message": "Welcome to Grand Things API - 大事记应用"}


# 健康检查
@app.get("/health")
async def health():
    return {"status": "healthy", "message": "大事记应用运行正常"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
