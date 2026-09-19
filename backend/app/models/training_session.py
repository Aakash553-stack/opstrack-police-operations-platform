from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Index, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    training_type: Mapped[str] = mapped_column(Text, nullable=False)
    instructor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(150), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    capacity: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "training_type IN ('firearms', 'legal', 'physical', 'cyber', 'first_aid', 'ethics')",
            name="ck_training_sessions_type",
        ),
        CheckConstraint("end_date >= start_date", name="ck_training_sessions_dates"),
        CheckConstraint("capacity > 0", name="ck_training_sessions_capacity"),
        Index("idx_training_sessions_start_date", "start_date"),
    )
