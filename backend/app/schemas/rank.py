from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RankBase(BaseModel):
    name: str = Field(max_length=50)
    level: int = Field(gt=0)


class RankCreate(RankBase):
    pass


class RankUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=50)
    level: int | None = Field(default=None, gt=0)


class RankRead(RankBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
