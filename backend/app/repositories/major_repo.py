import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.major import Major


async def get_active_majors(db: AsyncSession) -> list[Major]:
    """查询所有启用中的专业，用于计算推荐时加载 RIASEC profile。"""
    result = await db.execute(
        select(Major).where(Major.is_active == True)  # noqa: E712
    )
    return list(result.scalars())


async def get_major(db: AsyncSession, major_id: uuid.UUID) -> Major | None:
    """按 ID 查单个专业，找不到返回 None。"""
    return await db.get(Major, major_id)


async def list_majors(db: AsyncSession, search: str | None = None) -> list[Major]:
    """
    列出所有启用中的专业，支持按名称模糊搜索。
    search 为 None 时返回全部。
    """
    query = select(Major).where(Major.is_active == True)  # noqa: E712

    if search:
        query = query.where(Major.name.ilike(f"%{search}%"))

    result = await db.execute(query)
    return list(result.scalars())
