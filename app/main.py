from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.db import test_connection
from app.api import api_router
from app.core.config import Env, settings
from app.core.exceptions import register_exception_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("fastapi 启动")
    if settings.ENVIRONMENT == Env.local:
        print("本地开发模式启动: http://localhost:8000/api/v1  Control+C 停止")
        
    await test_connection()
    yield
    print("fastapi 停止")


# 创建app
app = FastAPI(
    title="API 服务 title",
    description="API 服务 desc",
    version="1.0.0",
    lifespan=lifespan
)
# 添加主 API 路由器
app.include_router(api_router)
register_exception_handlers(app)



