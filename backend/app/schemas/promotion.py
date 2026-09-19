from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PromotionBase(BaseModel):
    officer_id: int
    from_rank_id: int | None = None
    to_rank_id: int
    promotion_date: date
    approved_by_id: int | None = None
    notes: str | None = None


class PromotionCreate(PromotionBase):
    pass


class PromotionUpdate(BaseModel):
    notes: str | None = None


class PromotionRead(PromotionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
