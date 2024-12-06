from typing import Any
from sqlmodel import SQLModel, Field
from app.core.config import Env, settings

class RespModel[T](SQLModel):
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="", description="提示信息") 
    data: T | None = Field(default=None, description="数据")
    # 定义一个 attach 字段 值为 None 时 fastapi 响应时不返回此字段
    attach: Any | None = Field(default=None, description="附加数据", exclude=settings.ENVIRONMENT == Env.production)
