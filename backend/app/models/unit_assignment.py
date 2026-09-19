from datetime import date, datetime
from typing import Optional

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.enums import assignment_type_enum


class UnitAssignment(Base):
    __tablename__ = "unit_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    officer_id: Mapped[int] = mapped_column(ForeignKey("officers.id", ondelete="CASCADE"), nullable=False)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="RESTRICT"), nullable=False)
    assignment_type: Mapped[str] = mapped_column(assignment_type_enum, nullable=False, server_default="permanent")
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="ck_unit_assignments_dates"),
        Index("idx_unit_assignments_officer_id", "officer_id"),
        Index("idx_unit_assignments_unit_id", "unit_id"),
        Index(
            "uq_unit_assignments_open_officer",
            "officer_id",
            unique=True,
            postgresql_where=text("end_date IS NULL"),
        ),
    )
