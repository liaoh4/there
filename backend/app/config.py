from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str

    # Redis（有默认值，本地开发不设置也能用）
    REDIS_URL: str = "redis://localhost:6379/0"

    # 推荐专业数量
    TOP_N_RECOMMENDATIONS: int = 4

    # 跨域白名单：允许哪些前端地址访问后端
    ALLOWED_ORIGINS: list[str] = ["*"]

    # Neo4j（v2 用，现在不设置也不会报错）
    NEO4J_URL: str = ""

    # deep seek api
    DEEPSEEK_API_KEY: str = ""

    # 告诉 pydantic-settings 去哪里读配置
    # env_file：读取 .env 文件
    # extra="ignore"：.env 里有多余的变量时忽略，不报错
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
