from fastapi import APIRouter, Body
from app.models.base.Response import RespModel
from fastapi import HTTPException
from app.core.db import SessionDep
import re
import time
import random
from sqlmodel import Field, SQLModel



router = APIRouter()

@router.get("/")
async def login():
    return RespModel(
        data={
            "message": "Hello Login"
        }
    )




# 存储验证码和发送时间的字典
verification_codes = {}


@router.post("/send_code",
              response_model=RespModel[dict]
              )
async def send_verification_code(session: SessionDep,
                                 phone: str = Body(description="手机号呀", embed=True)
                                 ) :
    # 验证手机号格式
    if not re.match(r"^1[3-9]\d{9}$", phone):
        return RespModel(
            code=400,
            message="请输入正确的手机号",
            data=None
        )
    
    # 检查是否在60s内发送过验证码
    current_time = time.time()
    if phone in verification_codes:
        last_send_time = verification_codes[phone]["timestamp"]
        time_diff = current_time - last_send_time
        if time_diff < 60:
            remaining_time = int(60 - time_diff)
            return RespModel(
                code=400,
                message=f"请等待{remaining_time}秒后再试",
                data=None
            )

    # 生成4位随机验证码
    code = str(random.randint(1000, 9999))
    
    # 存储验证码和发送时间
    verification_codes[phone] = {
        "code": code,
        "timestamp": current_time
    }
    
   
    # 这里应该调用短信服务发送验证码
    
    return RespModel(
        code=200,
        message="验证码发送成功",
        data={
            "phone": phone,
            "expire_in": 60
        }
    )
