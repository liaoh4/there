import uuid

from pydantic import BaseModel, ConfigDict


class MajorDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    discipline_category: str
    major_category: str
    description: str | None = None
    riasec_r: float
    riasec_i: float
    riasec_a: float
    riasec_s: float
    riasec_e: float
    riasec_c: float


class MajorListResponse(BaseModel):
    total: int
    items: list[MajorDetail]
