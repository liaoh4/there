"""
Major catalogue endpoints.

GET /majors          → paginated list, optional ?search=keyword
GET /majors/{id}     → single major detail
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories import major_repo
from app.schemas.major import MajorDetail, MajorListResponse

router = APIRouter(prefix="/majors", tags=["majors"])


@router.get("", response_model=MajorListResponse)
async def list_majors(
    search: str | None = Query(None, description="按专业名称或学科类别模糊搜索"),
    db: AsyncSession = Depends(get_db),
) -> MajorListResponse:
    """Return all active majors, optionally filtered by search term."""
    majors = await major_repo.list_majors(db, search=search)
    return MajorListResponse(
        total=len(majors),
        items=[MajorDetail.model_validate(m) for m in majors],
    )


@router.get("/{major_id}", response_model=MajorDetail)
async def get_major(
    major_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MajorDetail:
    """Return a single major by ID."""
    major = await major_repo.get_major(db, major_id)
    if not major:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Major not found.")
    return MajorDetail.model_validate(major)
