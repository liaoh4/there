from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings


def _make_engine():
    settings = get_settings()
    return create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,   # 每次取连接前先 ping 一下，自动丢弃已断开的连接
        pool_size=10,         # 连接池保持 10 个连接
        max_overflow=20,      # 高峰期最多再额外创建 20 个
    )


engine = _make_engine()

# async_sessionmaker 是连接池上的会话工厂：每次调用它都能拿到一个新的数据库会话
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖注入用的数据库会话生成器。

    用法：
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...

    yield 之前：创建会话，开启事务
    yield：把会话交给路由函数使用
    yield 之后：自动提交（成功）或回滚（出错），关闭会话
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session
