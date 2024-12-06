from sqlmodel import SQLModel
from sqlalchemy import text
from .config import settings
import multiprocessing
from typing import AsyncGenerator, Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.tables import *

# 创建数据库引擎
cpu_count = multiprocessing.cpu_count()
workers = cpu_count * 2  # Gunicorn 工作进程数
max_db_conn = 2400  # Serverless 数据库最大连接数
# 每个工作进程的基本池大小
pool_size = max_db_conn // (workers * 2)  # 500 / (8 * 2) = 31
# 每个工作进程的最大溢出
max_overflow = pool_size  # 也是 31，总共 62


# 创建异步引擎
async_engine = create_async_engine(
    str(settings.database_url),
    pool_size=pool_size,
    max_overflow=max_overflow,
    pool_timeout=30,
    echo=True
)

 
# 通过 with 获取 session
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话

    Yields:
        AsyncGenerator[AsyncSession, None, None]: 数据库会话生成器
    """ 
    print("db.py get_async_session 获取数据库会话")
    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
            yield session

# 测试数据库连接
async def test_connection():
    """测试数据库连接是否成功"""
    print(f"db.py test_connection 测试数据库连接 {settings.database_url}")
    try:
        async with AsyncSession(bind=async_engine) as session:
            statement = text("SELECT 'hello'")
            result = await session.exec(statement)
            print(result.all())
            print("数据库连接测试成功")
            await session.close()
    except Exception as e:
        print(f"数据库连接测试失败: {str(e)}")
        raise Exception(f"数据库连接测试失败: {str(e)}")


# 异步初始化数据库
async def init_db() -> None:
    # 表应该通过 Alembic 迁移创建
    # 但是如果你不想使用迁移, 可以取消注释下面的行来创建表
    async with async_engine.begin() as conn:
        # from models.table import *  导入所有模型[文件顶部即可]
        # 标记
        # 确保在初始化数据库之前导入了所有 SQLModel 模型 (app.models)
        # 否则, SQLModel 可能无法正确初始化关系
        # 更多详细信息: https://github.com/tiangolo/full-stack-fastapi-template/issues/28
        print("创建所有表")
        await conn.run_sync(SQLModel.metadata.create_all)
    pass
    # 查找第一个超级用户
    # user = session.exec(
    #     select(User)
    #     .where(User.phone_number == settings.FIRST_SUPERUSER_PHONE_NUMBER)
    # ).first()

    # # 如果找不到超级用户, 则创建一个新的超级用户
    # # 在管理系统，超级用户使用 15200000001 + 密码登录
    # if not user:
    #     user_in = UserCreate(
    #         # email=settings.FIRST_SUPERUSER,
    #         password=settings.FIRST_SUPERUSER_PASSWORD,
    #         username=settings.FIRST_SUPERUSER,
    #         phone_number=settings.FIRST_SUPERUSER_PHONE_NUMBER,
    #         is_superuser=True,
    #     )
    #     user = crud.create_user(session=session, user_create=user_in)


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]