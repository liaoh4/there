import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import MajorCategory


async def get_sample_per_category(
    db: AsyncSession,
    category_codes: list[str],
    exclude_sample_codes: set[str] | None = None,
) -> dict[str, MajorCategory]:
    """
    For each given assessment category code, return one randomly sampled active
    MajorCategory. Prefers samples not in exclude_sample_codes; falls back to any
    available sample if all have been shown already.
    """
    result = await db.execute(
        select(MajorCategory).where(
            MajorCategory.assessment_category_code.in_(category_codes),
            MajorCategory.is_active.is_(True),
        )
    )
    all_rows = result.scalars().all()

    by_cat: dict[str, list[MajorCategory]] = {}
    for row in all_rows:
        by_cat.setdefault(row.assessment_category_code, []).append(row)

    out: dict[str, MajorCategory] = {}
    for code, items in by_cat.items():
        if not items:
            continue
        if exclude_sample_codes:
            fresh = [m for m in items if m.code not in exclude_sample_codes]
            out[code] = random.choice(fresh if fresh else items)
        else:
            out[code] = random.choice(items)
    return out


async def get_sub_majors_by_category_codes(
    db: AsyncSession,
    category_codes: list[str],
) -> dict[str, list[MajorCategory]]:
    """Return {assessment_category_code: [MajorCategory, ...]} for the given codes."""
    result = await db.execute(
        select(MajorCategory)
        .where(
            MajorCategory.assessment_category_code.in_(category_codes),
            MajorCategory.is_active.is_(True),
        )
        .order_by(MajorCategory.name)
    )
    rows = result.scalars().all()
    out: dict[str, list[MajorCategory]] = {}
    for row in rows:
        out.setdefault(row.assessment_category_code, []).append(row)
    return out


async def get_category_name_map(db: AsyncSession) -> dict[str, str]:
    """Return {assessment_category_code: assessment_category_name} for all active entries."""
    result = await db.execute(
        select(MajorCategory.assessment_category_code, MajorCategory.assessment_category_name)
        .where(MajorCategory.is_active.is_(True))
        .distinct()
    )
    return {code: name for code, name in result.all()}
