from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.enums import gender_enum, officer_status_enum


class Officer(Base):
    __tablename__ = "officers"

    id: Mapped[int] = mapped_column(primary_key=True)
    badge_number: Mapped[str] = mapped_column(String(15), nullable=False)
    first_name: Mapped[str] = mapped_column(String(60), nullable=False)
    last_name: Mapped[str] = mapped_column(String(60), nullable=False)
    gender: Mapped[str] = mapped_column(gender_enum, nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    date_joined: Mapped[date] = mapped_column(Date, nullable=False)
    rank_id: Mapped[int] = mapped_column(ForeignKey("ranks.id", ondelete="RESTRICT"), nullable=False)
    current_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("units.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(officer_status_enum, nullable=False, server_default="active")
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(CITEXT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("badge_number", name="uq_officers_badge_number"),
        UniqueConstraint("contact_email", name="uq_officers_contact_email"),
        CheckConstraint("badge_number ~ '^[A-Z]{2,4}-[0-9]{4,6}$'", name="ck_officers_badge_format"),
        CheckConstraint("date_joined > date_of_birth", name="ck_officers_joined_after_birth"),
        CheckConstraint(
            "date_joined >= date_of_birth + INTERVAL '18 years'", name="ck_officers_min_age"
        ),
        Index("idx_officers_rank_id", "rank_id"),
        Index("idx_officers_current_unit_id", "current_unit_id"),
        Index(
            "idx_officers_active_unit",
            "current_unit_id",
            postgresql_where=text("status = 'active'"),
        ),
    )
