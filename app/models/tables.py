from datetime import datetime, timedelta

from sqlmodel import SQLModel, Field

from app.models.schemas.user import UserBase


###=======================
### 登录记录表
###=======================
class LoginRequestRecord(SQLModel, table=True):
    # 主键设置成自增长
    id: int | None = Field(default=None, primary_key=True)
    # 手机号
    phone: str = Field(default=None)
    # 创建时间
    created_at: datetime = Field(default_factory=datetime.now)

###=======================
### 用户表
###=======================
class User(UserBase, table=True):
    pass

###=======================
### 短信验证码记录表
###=======================
class SMSCodeRecord(SQLModel, table=True):
    __tablename__ = "sms_code_records"

    # 主键设置成自增长
    id: int | None = Field(default=None, primary_key=True)
    # 手机号
    phone: str = Field(index=True)
    # 验证码
    code: str
    # ip地址
    ip_address: str = Field(index=True)
    # 创建时间
    created_at: datetime = Field(default_factory=datetime.now)
    # 过期时间 默认60s
    expires_at: datetime = Field(default_factory=lambda: datetime.now() + timedelta(seconds=60))

    # 判断是否过期
    def is_expired(self) -> bool:
        return self.expires_at < datetime.now()

    # 判断是否超过5分钟
    def is_expired_5_minutes(self) -> bool:
        return self.created_at < datetime.now() - timedelta(minutes=5)

    # 在 60s 内的话，还剩多少秒
    def remaining_seconds(self) -> int:
        return (self.expires_at - datetime.now()).seconds
