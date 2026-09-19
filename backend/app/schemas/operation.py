from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import OperationStatusEnum, OperationTypeEnum


class OperationBase(BaseModel):
    name: str = Field(max_length=150)
    operation_type: OperationTypeEnum
    status: OperationStatusEnum = OperationStatusEnum.planned
    lead_unit_id: int
    start_date: date
    end_date: date | None = None
    description: str | None = None


class OperationCreate(OperationBase):
    pass


class OperationUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=150)
    status: OperationStatusEnum | None = None
    end_date: date | None = None
    description: str | None = None


class OperationRead(OperationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
