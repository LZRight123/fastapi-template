from fastapi import APIRouter, Body, Request
from app import crud
from app.models.response import RespModel
from app.core.db import AsyncSessionDep
import re
from app.core.exceptions import ErrorEnum, ErrorModel
from app.models.tables import User, SMSCodeRecord
from app.tools import random
from app.tools.index import create_access_token


router = APIRouter()

@router.get("/")
async def login():
    return RespModel(
        data={
            "message": "Hello Login"
        }
    )


@router.post("/send_sms_code",
              response_model=RespModel[dict]
              )
async def send_verification_code(
    request: Request,
    session: AsyncSessionDep,
    phone: str = Body(description="手机号呀", embed=True)
) :
    """
    发送短信验证码给手机号注册的用户
    验证码60秒内只能请求一次，请勿重复请求。
    """
    # 验证手机号格式
    if not re.match(r"^1[3-9]\d{9}$", phone):
        return RespModel(code=400, message="请输入正确的手机号")
    
    # 获取客户端IP地址
    client_ip = request.client.host
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        proxy_ips = x_forwarded_for.split(',')
        client_ip = proxy_ips[-1].strip()

      
    sms_code_records_in_ip = await crud.get_sms_code_records_by_ip(client_ip, session)
    # 检查同ip地址的验证码记录是否在60s内发送过
    for record in sms_code_records_in_ip:
        if not record.is_expired():
            return RespModel(
                code=400,
                message=f"ip调用过于频繁，请{record.remaining_seconds()}秒后再试",
                data=None
            )

    # 检查手机号是否在60s内发送过验证码
    sms_code_records_in_phone = await crud.get_sms_code_records_by_phone(phone, session)
    for record in sms_code_records_in_phone:
        if not record.is_expired():
            return RespModel(
                code=400,
                message=f"手机号调用过于频繁，请{record.remaining_seconds()}秒后再试",
                data=None
            )
    
    # 生成4位随机验证码
    code =  random.generate_random_sms_code()
    # 这里应该调用短信服务发送验证码

    # 添加短信验证码发送记录
    sms_code_record = SMSCodeRecord(phone=phone, code=code, ip_address=client_ip)
    print("sms_code_record is: ", sms_code_record)
    await crud.add_sms_code_record(sms_code_record, session)
    
    return RespModel(
        code=200,
        message="验证码发送成功",
        data=sms_code_record
    )


# 实现手机号验证码登录
@router.post("/login_by_phone", response_model=RespModel)
async def login_by_phone(
    session: AsyncSessionDep,
    phone: str = Body(),
    code: str = Body(),
):
    """手机号验证码登录"""
    # 1. 检查登录频率限制
    recent_attempts = await crud.get_login_request_records_by_phone(phone, session)
    if len(recent_attempts) >= 5:
        raise Exception(ErrorModel(
            message="登录尝试过于频繁，请稍后再试",
            error_type=ErrorEnum.normal
        ))

    # 2. 获取最近的验证码记录
    latest_code_record = await crud.get_latest_sms_code_record_by_phone(phone, session)
    if not latest_code_record:
        raise Exception(ErrorModel(
            message="验证码不存在",
            error_type=ErrorEnum.normal
        ))
        
    # 3. 验证码匹配检查
    if latest_code_record.code != code:
        raise Exception(ErrorModel(
            message="无效验证码",
            error_type=ErrorEnum.normal
        ))

    # 4. 验证码过期检查
    if latest_code_record.is_expired_5_minutes():
        raise Exception(ErrorModel(
            message="验证码已过期",
            error_type=ErrorEnum.normal
        ))

    # # # 5. 获取或创建用户
    user = await crud.get_user_by_phone(phone, session)

    if not user:
        # 创建新用户
        user = User(
            phone=phone,
            username=random.generate_random_username(),
            invite_code=random.generate_random_invite_code()
         )
        await crud.create_user(user, session)
 
    # 6. 根据用户 id 生成JWT访问令牌
    token_model = create_access_token(user.id)


    # 7. 返回令牌
    return RespModel(
        code=200,
        message="登录成功",
        data= token_model
    )
