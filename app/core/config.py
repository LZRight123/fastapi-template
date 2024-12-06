from enum import Enum
from pydantic_settings import BaseSettings , SettingsConfigDict 
from pydantic import computed_field, PostgresDsn
from pydantic_core import MultiHostUrl

# 环境变量 production | staging | local 生产 | 测试 | 本地
class Env(str, Enum):
    production = "production"
    staging = "staging"
    local = "local"

class Settings(BaseSettings):
    # 从.env文件读取环境变量
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

    # 环境变量
    ENVIRONMENT: Env = Env.production
    
    # JWT 配置
    SECRET_KEY: str # 从.env文件读取
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 # 默认30天

    # 数据库配置
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    API_V1_STR: str = "/api/v1"


    @computed_field  # type: ignore[misc]
    def database_url(self) -> PostgresDsn:
        # 构建 PostgreSQL 数据库连接 URI
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )
    

settings: Settings = Settings()
