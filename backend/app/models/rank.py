from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Rank(Base):
    __tablename__ = "ranks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("name", name="uq_ranks_name"),
        UniqueConstraint("level", name="uq_ranks_level"),
        CheckConstraint("level > 0", name="ck_ranks_level_positive"),
    )
