from datetime import datetime
from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    # 过期时间
    expires: datetime
    token_type: str = "bearer"
