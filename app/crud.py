from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timedelta
from app.models.tables import SMSCodeRecord
from app.models.tables import User
from app.models.tables import LoginRequestRecord


###===========================================
### 用户相关
###===========================================
# 根据用户id查询用户
async def get_user_by_id(user_id: str, session: AsyncSession) -> User | None:
    statement = select(User).where(User.id == user_id)
    result = await session.exec(statement)
    return result.first()

# 查询前 100 个用户
async def get_first_100_users(session: AsyncSession) -> list[User]:
    statement = select(User).order_by(User.created_at.desc()).limit(100)
    result = await session.exec(statement)
    return result.all()

# 根据用户名查询用户
async def get_user_by_username(username: str, session: AsyncSession) -> User | None:
    statement = select(User).where(User.username == username)
    result = await session.exec(statement)
    return result.first()

# 更新用户信息
async def update_user(user: User, session: AsyncSession) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

###===========================================
### 登录相关
###===========================================
# 查询 LoginRequestRecord 表中最近1分钟内，该手机号发送的登录请求记录
async def get_login_request_records_by_phone(phone: str, session: AsyncSession) -> list[LoginRequestRecord]:
    statement = select(LoginRequestRecord).where(LoginRequestRecord.phone == phone, LoginRequestRecord.created_at >= datetime.now() - timedelta(minutes=1))
    result = await session.exec(statement)
    return result.all()

# 根据手机号查询用户
async def get_user_by_phone(phone: str, session: AsyncSession) -> User | None:
    statement = select(User).where(User.phone == phone)
    result = await session.exec(statement)
    return result.first()

# 创建一个新用户
async def create_user(user: User, session: AsyncSession) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


###===========================================
### 短信验证码相关
###===========================================
# 查询数据库中该ip地址对应的验证码记录
async def get_sms_code_records_by_ip(ip_address: str, session: AsyncSession) -> list[SMSCodeRecord]:
    statement = select(SMSCodeRecord).where(SMSCodeRecord.ip_address == ip_address)
    result = await session.exec(statement)
    return result.all()

# 查询数据库中该手机号对应的验证码记录
async def get_sms_code_records_by_phone(phone: str, session: AsyncSession) -> list[SMSCodeRecord]:
    statement = select(SMSCodeRecord).where(SMSCodeRecord.phone == phone)
    result = await session.exec(statement)
    return result.all()

# 添加短信验证码发送记录
async def add_sms_code_record(sms_code_record: SMSCodeRecord, session: AsyncSession) -> SMSCodeRecord:
    session.add(sms_code_record)
    await session.commit()
    await session.refresh(sms_code_record)
    return sms_code_record

# 获取最近的一条 该手机号发送的验证码记录
async def get_latest_sms_code_record_by_phone(phone: str, session: AsyncSession) -> SMSCodeRecord | None:
    statement = select(SMSCodeRecord).where(SMSCodeRecord.phone == phone).order_by(SMSCodeRecord.created_at.desc())
    result = await session.exec(statement)
    return result.first()