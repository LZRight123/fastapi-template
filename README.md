### 用此模版
1. 初始化依赖
```shell
python3 -m venv .venv
source .venv/bin/activate
poetry install
```

2. 修改 .env 文件数据库配置
3. 本地运行
```shell
# docker 启动
docker compose -f docker-compose-local.yml up -d
# --build 重新构建
# or python 启动
sh start.sh
```


### 从 0 到 1 搭建
- 项目环境配置
    1. 新建项目 `mkdir xxx` 使用 cursor vscode，需要 `cursor`  帮你写可以配置 `.cursorrules` https://github.com/PatrickJS/awesome-cursorrules 
        
        ```python
        # 项目目录
        #1. 创建python 虚拟环境
        python3 -m venv .venv
        #2. 激活虚拟环境:
        source .venv/bin/activate 
        #3. 退出虚拟环境:
        deactivate
        
        # 可以直接 Cmd+Shift+P 后输入 Python: Select Interpreter 选择或者新建虚拟环境
        #cursor or vscode 运行 py 文件 setting.json 添加：
            "python.pythonPath": "/path/to/your/python",
            "python.terminal.activateEnvironment": true,
            "python.linting.enabled": true,
            "python.formatting.provider": "autopep8"
        
        ```
        
    2. 使用 `poetry` 来进行包管理 `poetry init` 创建 `pyproject.toml` 
    3. `poetry add`  添加依赖，用 unicorn 来运行
        
        ```bash
        poetry add uvicorn fastapi
        ```
        
        ```python
        if __name__ == '__main__':
            uvicorn.run(
                app="main:app",
                host='127.0.0.1',
                port=1234,
                reload=True
            )
        ```
        
- 配置环境变量
    1. 在项目目录下新建 `.env` 不要上传 git
        
        ```
        # Postgres
        POSTGRES_SERVER=localhost
        POSTGRES_PORT=5432
        POSTGRES_DB=app
        POSTGRES_USER=liseami
        POSTGRES_PASSWORD=rememberYOU1
        ```
        
    2. 添加依赖库 `python-dotenv` `pydantic-settings` 
        
        ```bash
        poetry add python-dotenv pydantic-settings  
        ```
        
    3. 在 `/app/core/` 下新建 [`config.py`](http://config.py) 并获取环境变量
        
        ```python
        from dotenv import load_dotenv
        from pydantic import PostgresDsn, computed_field
        from pydantic_core import MultiHostUrl
        from pydantic_settings import BaseSettings, SettingsConfigDict
        
        class Settings(BaseSettings):
            POSTGRES_SERVER: str
            POSTGRES_PORT: int = 5432
            POSTGRES_DB: str
            POSTGRES_USER: str
            POSTGRES_PASSWORD: str
        
            model_config = SettingsConfigDict(
                env_file=".env",
                env_ignore_empty=True,
                extra="ignore"
            )
        
            # 数据库连接URL
            @computed_field  # type: ignore[misc]
            def dataBaseURI(self) -> PostgresDsn:
                # 构建 PostgreSQL 数据库连接 URI
                return MultiHostUrl.build(
                    scheme="postgresql+asyncpg", # 异步
                    scheme="postgresql+psycopg",
                    username=self.POSTGRES_USER,
                    password=self.POSTGRES_PASSWORD,
                    host=self.POSTGRES_SERVER,
                    port=self.POSTGRES_PORT,
                    path=self.POSTGRES_DB,
                )
        
        load_dotenv()
        settings = Settings()
        
        if __name__ == "__main__":
            print(settings.dataBaseURI)
        ```
        
- 连接数据库 `RDS` 或者 本地 docker
    1. 添加 [`sqlmodel`](https://sqlmodel.tiangolo.com/) 依赖
        
        ```bash
        # 异步
        poetry add sqlmodel, asyncpg, greenlet
        # 同步
        poetry add sqlmodel, psycopg, psycopg-binary
        ```
        
    2. 进行数据库连接 `db.py`
        
        ```python
        from typing import AsyncGenerator, Annotated
        from fastapi import Depends
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlmodel.ext.asyncio.session import AsyncSession
        from sqlalchemy.orm import sessionmaker
        
        # 创建数据库引擎
        cpu_count = multiprocessing.cpu_count()
        workers = cpu_count * 2  # Gunicorn 工作进程数
        max_db_conn = 2400  # Serverless 数据库最大连接数
        # 每个工作进程的基本池大小
        pool_size = max_db_conn // (workers * 2)  # 500 / (8 * 2) = 31
        # 每个工作进程的最大溢出
        max_overflow = pool_size  # 也是 31，总共 62
        
        # 测试数据库连接
        async def test_connection():
            """测试数据库连接是否成功"""
            try:
                async with AsyncSession(bind=async_engine) as session:
                    statement = text("SELECT 'hello'")
                    result = await session.exec(statement)
                    print(result.all())
                    print("数据库连接测试成功")
            except Exception as e:
                print(f"数据库连接测试失败: {str(e)}")
                raise Exception(f"数据库连接测试失败: {str(e)}")
        
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
            try:
                async with async_session() as session:
                    yield session
            except Exception as e:
                raise Exception(f"数据库连接失败: {str(e)}")
                        
        SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
        ```
        
        ```python
        import multiprocessing
        from collections.abc import Generator
        from contextlib import contextmanager
        from typing import Annotated
        
        from fastapi import Depends
        from sqlmodel import Session, create_engine
        
        from app.core.config import settings
        
        cpu_count = multiprocessing.cpu_count() * 2
        workers = cpu_count
        max_db_conn = 500
        pool_size = max_db_conn // (workers * 2)
        max_overflow = pool_size
        engine = create_engine(
            str(settings.dataBaseURI),
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=30,
            echo=True
        )
        
        # 测试数据库连接
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
        
        # 通过 with 获取 session
        def get_session() -> Generator[Session, None, None]:
            """获取数据库会话
        
            Yields:
                Generator[Session, None, None]: 数据库会话生成器
        
            Raises:
                Exception: 数据库连接或会话创建失败时抛出异常
            """
            print("db.py get_session 获取数据库会话")
            try:
                with Session(engine) as session:
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
        
        # fastApi 依赖注入
        SessionDep = Annotated[Session, Depends(get_db)]
        ```
        
    3. 执行数据库操作，`fastApi` 依赖注入和非 `fastApi` 获取 `session`
        
        ```python
        @app.get("/")
        async def root(session: SessionDep):
            current_db = session.execute(text("SELECT current_database();")).scalar_one()
            print(f"Current Database: {current_db}")
            session.close()
            return {"message": "Hello World"}
        
        def test_sql():
            print(settings.dataBaseURI)
        
            with get_temp_db() as session:
                current_db = session.execute(text("SELECT current_database();")).scalar_one()
                print(f"Current Database: {current_db}")
                session.close()
                sql = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
                result = session.execute(sql)
                for row in result:
                    print(row)
        ```
        
- 配置 `fastapi`
    1. 配置路由：新建 `api` 文件夹，`__init__.py` 文件。根据业务需求在 `api` 文件夹下新建 `login.py` `user.py` 等
        
        ```python
        from fastapi import APIRouter
        from core.config import settings
        from models.base.Response import RespModel
        from . import login, user, ai
        
        api_router = APIRouter()
        
        base_router = APIRouter(prefix=settings.API_V1_STR)
        base_router.include_router(user.router, prefix="/user", tags=["user"])
        base_router.include_router(login.router, prefix="/login", tags=["login"])
        base_router.include_router(ai.router, prefix="/ai", tags=["ai"])
        
        api_router.include_router(base_router)
        @api_router.get("/")
        async def root() -> RespModel[dict]:
            return RespModel(
                data={
                    "message": "请检查 path - root"
                }
            )
        
        @base_router.get("/")
        async def root() -> RespModel[dict]:
            return RespModel(
                data={
                    "message": "请检查 path - base"
                }
            )
        ```
        
        ```python
        router = APIRouter()
        
        @router.get("/request_sms_code", summary="发送登录验证码")
        async def request_sms_code(
                session: SessionDep,
        ):
            return {"message": "发送登录验证码"}
        
        ```
        
        ```python
        @router.get("/me", summary="获取用户信息")
        async def request_sms_code(
                session: SessionDep,
        ):
            return {"message": "获取用户信息"}
        ```
        
        ```python
        from contextlib import asynccontextmanager
        from fastapi import FastAPI
        import uvicorn
        from core.db import test_connection, init_db
        from api import api_router
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            print("fastapi 启动")
            await test_connection()
            yield
            print("fastapi 停止")
        
        # 创建app
        app = FastAPI(
            title="API 服务 title",
            description="API 服务 desc",
            version="1.0.0",
            lifespan=lifespan
        )
        # 添加主 API 路由器，指定前缀为 API_V1_STR
        app.include_router(api_router)
        
        # 运行app
        if __name__ == "__main__":
            print("启动: http://localhost:8000/api/v1  Control+C 停止")
            uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
        ```
        
- 配置 `ORM` 及使用 [alembic](https://alembic.sqlalchemy.org/) 数据库迁移
    
    ```bash
    poetry add alembic
    alembic init -t async app/migrations
    
    # 迁移脚本命名最佳实践 添加日期前缀 使用清晰的描述性名称
    # 1. 创建迁移脚本
    alembic revision --autogenerate -m "20240125_create_xx_table"
    # 执行迁移
    # 1. 升级到最新版本
    alembic upgrade head
    # 回滚到特定版本:
    alembic downgrade -1  # 回滚一个版本
    alembic downgrade <revision>  # 回滚到指定版本
    
    # 查看历史
    alembic history
    # 只查看头版本（最新版本）
    alembic heads
    # 查看当前
    alembic current
    # 检查迁移状态
    alembic check
    ```
    
    `alembic init` 后生成文件结构如下
    
    ```bash
    /app
     -- alembic.ini # 读取基础配置，可以在里面修改 sqlalchemy.url 也可以放到 env.py 里改
    	 /migrations 
    	  # 迁移脚本模板文件，使用这个模板来生成新的迁移脚本文件。import sqlmodel 即可
    	  -- script.py.mako
    	  # 环境配置文件，作用如下：
    	  # 1. 建立数据库连接
    	  # 2. 配置迁移环境
    	  # 3. 加载 SQLAlchemy 模型
    		# 4. 控制迁移运行方式
    		# 5. 提供迁移上下文
    		-- env.py # 
     
    ```
    
    ```python
    # from alembic import context
    # 导入所有的 table model
    from app.models.tables import *
    from sqlmodel import SQLModel
    from app.core.db import settings
    
    database_url = str(settings.database_url)
    # this is the Alembic Config object, which provides
    # access to the values within the .ini file in use.
    config = context.config
    # 从本地 Config 中取 database_url 覆盖 .ini 文件中的 sqlalchemy.url
    config.set_main_option('sqlalchemy.url', database_url)
    # 设置 target_metadata
    target_metadata = SQLModel.metadata
    ```