from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin


class MajorCategory(UUIDMixin, Base):
    """93 专业类，用于兴趣选择阶段展示给用户。每个专业类归属 18 大类之一。"""

    __tablename__ = "major_categories"

    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    assessment_category_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    assessment_category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    typical_representatives: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
