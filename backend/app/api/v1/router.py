from fastapi import APIRouter

from app.api.v1 import assessments, majors

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(assessments.router)
api_router.include_router(majors.router)