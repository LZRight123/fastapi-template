from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from app.core.db import test_connection, init_db
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("fastapi 启动")
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
