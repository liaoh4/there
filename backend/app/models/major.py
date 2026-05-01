from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Major(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "majors"

    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    discipline_category: Mapped[str] = mapped_column(String(50), nullable=False)  # 学科门类，如"工学"
    major_category: Mapped[str] = mapped_column(String(50), nullable=False)       # 专业类，如"计算机类"
    description: Mapped[str | None] = mapped_column(Text)

    # 软删除标志：历史推荐记录持有 major_id 外键，硬删除会破坏引用完整性
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # RIASEC profile：6 个独立列，Numeric(3,2) 表示最多3位数字、2位小数，即 0.00–9.99
    # 实际范围是 0.00–1.00，用独立列而非 JSON 是为 v2 pgvector 余弦查询预留空间
    riasec_r: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    riasec_i: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    riasec_a: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    riasec_s: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    riasec_e: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    riasec_c: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)

    @property
    def riasec_vector(self) -> list[float]:
        """以浮点数列表返回 RIASEC 向量，供 scoring 服务做余弦计算。"""
        return [
            float(self.riasec_r), float(self.riasec_i), float(self.riasec_a),
            float(self.riasec_s), float(self.riasec_e), float(self.riasec_c),
        ]
