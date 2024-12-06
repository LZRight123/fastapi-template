from fastapi import APIRouter
from app.core.config import settings
from app.models.response import RespModel
from app.models.schemas.product import Product
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
            "environment": settings.ENVIRONMENT,
        }
    )

@base_router.get("/")
async def base():
    return RespModel(
        data={
            "message": "请检查 path - base"
        }
    )

@base_router.get("/configs")
async def base():
    return RespModel(
        data={
            "products": [Product(id=type[0], name=type[1], type=Product.ProductType.monthly) for type in Product.ProductType]
        }   
    )

api_router.include_router(base_router)
