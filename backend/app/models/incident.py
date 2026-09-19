from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.enums import incident_severity_enum


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_number: Mapped[str] = mapped_column(String(20), nullable=False)
    incident_type: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(incident_severity_enum, nullable=False, server_default="low")
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="reported")
    reported_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    location_description: Mapped[str] = mapped_column(String(200), nullable=False)
    reporting_officer_id: Mapped[int] = mapped_column(
        ForeignKey("officers.id", ondelete="RESTRICT"), nullable=False
    )
    assigned_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("units.id", ondelete="SET NULL"), nullable=True
    )
    operation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("operations.id", ondelete="SET NULL"), nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("incident_number", name="uq_incidents_incident_number"),
        CheckConstraint(
            "incident_type IN ('theft', 'assault', 'traffic', 'homicide', 'fraud', "
            "'public_disturbance', 'other')",
            name="ck_incidents_type",
        ),
        CheckConstraint(
            "status IN ('reported', 'under_investigation', 'resolved', 'closed')",
            name="ck_incidents_status",
        ),
        Index("idx_incidents_assigned_unit_id", "assigned_unit_id"),
        Index("idx_incidents_reporting_officer_id", "reporting_officer_id"),
        Index("idx_incidents_operation_id", "operation_id"),
        Index(
            "idx_incidents_open",
            "status",
            postgresql_where=text("status IN ('reported', 'under_investigation')"),
        ),
    )
