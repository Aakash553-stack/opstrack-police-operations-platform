from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import UserRoleEnum


class UserBase(BaseModel):
    officer_id: int | None = None
    username: str = Field(max_length=100)
    role: UserRoleEnum = UserRoleEnum.officer
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    role: UserRoleEnum | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
