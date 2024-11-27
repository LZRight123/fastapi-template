# 同步数据库
# 优先用异步

# 创建数据库引擎
import multiprocessing
from typing import Annotated, Generator
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlmodel import SQLModel, Session
from .config import settings

__cpu_count = multiprocessing.cpu_count()
__workers = __cpu_count * 2  # Gunicorn 工作进程数
__max_db_conn = 2400  # Serverless 数据库最大连接数
# 每个工作进程的基本池大小
__pool_size = __max_db_conn // (__workers * 2)  # 500 / (8 * 2) = 31
# 每个工作进程的最大溢出
__max_overflow = __pool_size  # 也是 31，总共 62

# 创建同步引擎
__engine = create_engine(
    str(settings.database_url),
    pool_size=__pool_size,
    max_overflow=__max_overflow,
    pool_timeout=30,
    echo=True
)

# 测试数据库连接# 同步测试数据库连接
def __test_connection():
    """测试数据库连接是否成功"""
    try:
        with Session(__engine) as session:
            statement = text("SELECT 'hello'")
            result = session.exec(statement)
            print(result.all())
            print("数据库连接测试成功")
    except Exception as e:
        print(f"数据库连接测试失败: {str(e)}")
        raise Exception(f"数据库连接测试失败: {str(e)}")
    

def __get_session() -> Generator[Session, None, None]:
    """获取数据库会话

    Yields:
        Generator[Session, None, None]: 数据库会话生成器

    Raises:
        Exception: 数据库连接或会话创建失败时抛出异常
    """
    print("db.py get_session 获取数据库会话")
    try:
        with Session(__engine) as session:
            try:
                yield session
                session.commit()
            except Exception as e:
                session.rollback()
                raise Exception(f"数据库会话操作失败: {str(e)}")
            finally:
                session.close()
    except Exception as e:
        raise Exception(f"数据库连接失败: {str(e)}")

# 同步初始化数据库
def __init_db():
    # 表应该通过 Alembic 迁移创建
    # 但是如果你不想使用迁移, 可以取消注释下面的行来创建表
    # from models.table import *  导入所有模型[文件顶部即可]
    # 标记
    # 确保在初始化数据库之前导入了所有 SQLModel 模型 (app.models)
    # 否则, SQLModel 可能无法正确初始化关系
    # 更多详细信息: https://github.com/tiangolo/full-stack-fastapi-template/issues/28
    # SQLModel.metadata.create_all(__engine)
    pass


__SessionDep = Annotated[Session, Depends(__get_session)]
