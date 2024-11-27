import os
from fastapi import APIRouter
from app.core.config import settings
from app.models.base.Response import RespModel
from . import login, user, ai


api_router = APIRouter()

# API_V1_STR=/api/v1
base_router = APIRouter(prefix=settings.API_V1_STR)
base_router.include_router(user.router, prefix="/user", tags=["user"])
base_router.include_router(login.router, prefix="/login", tags=["login"])
base_router.include_router(ai.router, prefix="/ai", tags=["ai"])

@api_router.get("/")
async def root():
    # 获取环境变量
    # env_dict = dict(os.environ)
    return RespModel(
        data={
            "message": "请检查 path - root",
        }
    )

@base_router.get("/")
async def base():
    return RespModel(
        data={
            "message": "请检查 path - base"
        }
    )

api_router.include_router(base_router)

