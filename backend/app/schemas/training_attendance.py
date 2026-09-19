from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import TrainingAttendanceStatusEnum


class TrainingAttendanceBase(BaseModel):
    training_session_id: int
    officer_id: int
    attendance_status: TrainingAttendanceStatusEnum = TrainingAttendanceStatusEnum.registered
    score: Decimal | None = Field(default=None, ge=0, le=100)
    certificate_issued: bool = False


class TrainingAttendanceCreate(TrainingAttendanceBase):
    pass


class TrainingAttendanceUpdate(BaseModel):
    attendance_status: TrainingAttendanceStatusEnum | None = None
    score: Decimal | None = Field(default=None, ge=0, le=100)
    certificate_issued: bool | None = None


class TrainingAttendanceRead(TrainingAttendanceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
