from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from pydantic import computed_field
from app.models.response import RespModel
from enum import Enum
from sqlmodel import Field, SQLModel
from sqlalchemy.exc import SQLAlchemyError

# 定义一个 pydantic 的 Enum 类型
class ErrorEnum(str, Enum):
    normal = "normal_error"
    vip_level = "vip_level_error"
    login = "login_error"

class ErrorModel(SQLModel):
    message: str = Field(default="", description="错误信息")
    error_type: ErrorEnum = Field(default=ErrorEnum.normal, description="错误类型")

    @computed_field
    def code(self) -> int:
        match self.error_type:
            case ErrorEnum.vip_level:
                return 403
            case ErrorEnum.login:
                return 401
            case _:
                return 400


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """处理 HTTP 异常"""
        return JSONResponse(
            status_code=400,
            content=RespModel(
                code=500,
                message=f"HTTPException:",
                data=exc.detail
            ).model_dump()
        )   
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        """处理 SQLAlchemy 异常"""
        return JSONResponse(
            status_code=503,
            content=RespModel(code=503, message=f"SQLAlchemyError: 数据库异常 {exc}", data=None).model_dump()
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """处理所有其他未捕获的异常"""

        # 判断 exc.args 有值，且第一个是否是 ErrorModel 类型
        if exc.args and isinstance(exc.args[0], ErrorModel):
            error_model = exc.args[0]
            return JSONResponse(
                status_code=error_model.code,
                content=error_model.model_dump()
            )
        else:
            return JSONResponse(
                status_code=400,
                content=RespModel(
                    code=500,
                    message=f"Exception: {exc}",
                    data=None
                ).model_dump()
            )
