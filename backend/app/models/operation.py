from datetime import date, datetime
from typing import Optional

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.enums import operation_type_enum


class Operation(Base):
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    operation_type: Mapped[str] = mapped_column(operation_type_enum, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="planned")
    lead_unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="RESTRICT"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('planned', 'active', 'completed', 'cancelled')", name="ck_operations_status"
        ),
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="ck_operations_dates"),
        Index("idx_operations_lead_unit_id", "lead_unit_id"),
        Index(
            "idx_operations_active",
            "status",
            postgresql_where=text("status IN ('planned', 'active')"),
        ),
    )
