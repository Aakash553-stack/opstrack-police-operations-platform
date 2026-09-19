from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class TrainingAttendance(Base):
    __tablename__ = "training_attendance"

    id: Mapped[int] = mapped_column(primary_key=True)
    training_session_id: Mapped[int] = mapped_column(
        ForeignKey("training_sessions.id", ondelete="CASCADE"), nullable=False
    )
    officer_id: Mapped[int] = mapped_column(ForeignKey("officers.id", ondelete="CASCADE"), nullable=False)
    attendance_status: Mapped[str] = mapped_column(Text, nullable=False, server_default="registered")
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    certificate_issued: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "attendance_status IN ('registered', 'attended', 'absent', 'excused')",
            name="ck_training_attendance_status",
        ),
        CheckConstraint(
            "score IS NULL OR (score >= 0 AND score <= 100)", name="ck_training_attendance_score"
        ),
        UniqueConstraint("training_session_id", "officer_id", name="uq_training_attendance"),
        Index("idx_training_attendance_officer_id", "officer_id"),
    )
