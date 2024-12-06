from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    id: UUID | None = Field(
        default_factory=uuid4,
        primary_key=True,
    )
    # 手机号
    phone: str | None = Field(default=None, index=True, exclude=False)
    # 用户名
    username: str | None = Field(default=None)
    # 创建时间
    created_at: datetime = Field(
        default_factory=datetime.now,
    )
    # 更新时间 此字段不返回给前端
    updated_at: datetime = Field(
        default_factory=datetime.now,
    )
    # 邀请码
    invite_code: str | None = Field(default=None, index=True, unique=True)


class UserOut(UserBase):
    sign: str = "--"
    fuck: str = "fuck"

class UserUpdate(SQLModel):
    username: str  = ""
    avatar: str  = ""
    phone: str = ""