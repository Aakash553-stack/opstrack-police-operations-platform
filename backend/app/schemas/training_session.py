from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import TrainingTypeEnum


class TrainingSessionBase(BaseModel):
    title: str = Field(max_length=150)
    training_type: TrainingTypeEnum
    instructor_name: str = Field(max_length=100)
    location: str = Field(max_length=150)
    start_date: date
    end_date: date
    capacity: int = Field(gt=0)


class TrainingSessionCreate(TrainingSessionBase):
    pass


class TrainingSessionUpdate(BaseModel):
    location: str | None = Field(default=None, max_length=150)
    capacity: int | None = Field(default=None, gt=0)


class TrainingSessionRead(TrainingSessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
