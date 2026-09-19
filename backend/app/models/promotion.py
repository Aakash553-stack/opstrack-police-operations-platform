from datetime import date, datetime
from typing import Optional

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(primary_key=True)
    officer_id: Mapped[int] = mapped_column(ForeignKey("officers.id", ondelete="RESTRICT"), nullable=False)
    from_rank_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ranks.id", ondelete="RESTRICT"), nullable=True
    )
    to_rank_id: Mapped[int] = mapped_column(ForeignKey("ranks.id", ondelete="RESTRICT"), nullable=False)
    promotion_date: Mapped[date] = mapped_column(Date, nullable=False)
    approved_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("officers.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("from_rank_id IS DISTINCT FROM to_rank_id", name="ck_promotions_rank_change"),
        Index("idx_promotions_officer_id", "officer_id"),
        Index("idx_promotions_promotion_date", "promotion_date"),
    )
