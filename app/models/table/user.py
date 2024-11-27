
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column
from sqlmodel import Field, SQLModel
import sqlalchemy.dialects.postgresql as pg

class User(SQLModel, table=True):
    id: UUID | None = Field(
        default_factory=uuid4,
        primary_key=True,
    )
    username: str = Field(default=None)
    password: str = Field(default=None)
    created_at: datetime = Field(
        default_factory=datetime.now,
    )
    updated_at: datetime = datetime.now()

