from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.enums import shift_enum


class Patrol(Base):
    __tablename__ = "patrols"

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="RESTRICT"), nullable=False)
    officer_id: Mapped[int] = mapped_column(ForeignKey("officers.id", ondelete="RESTRICT"), nullable=False)
    patrol_date: Mapped[date] = mapped_column(Date, nullable=False)
    shift: Mapped[str] = mapped_column(shift_enum, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    vehicle_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    area_description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="scheduled")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'in_progress', 'completed', 'cancelled')", name="ck_patrols_status"
        ),
        CheckConstraint("end_time > start_time", name="ck_patrols_times"),
        Index("idx_patrols_officer_id", "officer_id"),
        Index("idx_patrols_unit_id", "unit_id"),
        Index("idx_patrols_patrol_date", "patrol_date"),
    )
