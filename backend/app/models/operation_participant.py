from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class OperationParticipant(Base):
    __tablename__ = "operation_participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    operation_id: Mapped[int] = mapped_column(
        ForeignKey("operations.id", ondelete="CASCADE"), nullable=False
    )
    officer_id: Mapped[int] = mapped_column(ForeignKey("officers.id", ondelete="RESTRICT"), nullable=False)
    role_in_operation: Mapped[str] = mapped_column(Text, nullable=False, server_default="participant")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "role_in_operation IN ('lead', 'participant', 'support')",
            name="ck_operation_participants_role",
        ),
        UniqueConstraint("operation_id", "officer_id", name="uq_operation_participants"),
        Index("idx_operation_participants_officer_id", "officer_id"),
    )
