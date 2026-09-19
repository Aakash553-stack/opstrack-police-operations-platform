from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import UnitTypeEnum


class UnitBase(BaseModel):
    name: str = Field(max_length=100)
    unit_type: UnitTypeEnum
    parent_unit_id: int | None = None


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    unit_type: UnitTypeEnum | None = None
    parent_unit_id: int | None = None


class UnitRead(UnitBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
