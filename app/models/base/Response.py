from sqlmodel import SQLModel, Field


class RespModel[T](SQLModel):
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="", description="提示信息") 
    data: T | None = Field(default=None, description="数据")
