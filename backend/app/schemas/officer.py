from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.enums import GenderEnum, OfficerStatusEnum


class OfficerBase(BaseModel):
    badge_number: str = Field(pattern=r"^[A-Z]{2,4}-[0-9]{4,6}$", max_length=15)
    first_name: str = Field(max_length=60)
    last_name: str = Field(max_length=60)
    gender: GenderEnum
    date_of_birth: date
    date_joined: date
    rank_id: int
    current_unit_id: int | None = None
    status: OfficerStatusEnum = OfficerStatusEnum.active
    contact_phone: str | None = Field(default=None, max_length=20)
    contact_email: EmailStr | None = None


class OfficerCreate(OfficerBase):
    pass


class OfficerUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=60)
    last_name: str | None = Field(default=None, max_length=60)
    rank_id: int | None = None
    current_unit_id: int | None = None
    status: OfficerStatusEnum | None = None
    contact_phone: str | None = Field(default=None, max_length=20)
    contact_email: EmailStr | None = None


class OfficerRead(OfficerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
