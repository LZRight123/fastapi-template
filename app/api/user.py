from uuid import uuid4
from fastapi import APIRouter, Depends
from sqlmodel import select
from app.models.table.user import User
from app.core.db import SessionDep
from sqlalchemy import text
from app.models.base.Response import RespModel

router = APIRouter()

@router.get("/info")
async def get_user_info(session: SessionDep) -> RespModel[list[dict]]:
    statement = select(User).order_by(User.created_at.desc())
    result = await session.exec(statement)
    data = result.all()
    
    return RespModel(
        code=200,
        message="获取用户信息成功",
        data=data,
    )
 
@router.get("/create")
async def create_user(session:  SessionDep) -> RespModel[dict]:
    user = User(
        username="test_user", 
        password="test_password")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return RespModel(
        code=200,
        message="创建用户成功",
        data=user
    )