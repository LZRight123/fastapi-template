
from uuid import UUID, uuid4
from sqlalchemy import Column
from sqlmodel import Field, SQLModel
import sqlalchemy.dialects.postgresql as pg

class Login(SQLModel, table=True):
    id: UUID = Field(
        default=None,
        primary_key=True,
    )
    title: str = Field(default=None)
    author: str
