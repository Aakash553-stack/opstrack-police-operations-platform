from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import PatrolStatusEnum, ShiftEnum


class PatrolBase(BaseModel):
    unit_id: int
    officer_id: int
    patrol_date: date
    shift: ShiftEnum
    start_time: time
    end_time: time
    vehicle_code: str | None = Field(default=None, max_length=20)
    area_description: str | None = Field(default=None, max_length=200)
    status: PatrolStatusEnum = PatrolStatusEnum.scheduled


class PatrolCreate(PatrolBase):
    pass


class PatrolUpdate(BaseModel):
    status: PatrolStatusEnum | None = None
    area_description: str | None = Field(default=None, max_length=200)


class PatrolRead(PatrolBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
