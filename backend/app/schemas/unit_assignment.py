from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.enums import AssignmentTypeEnum


class UnitAssignmentBase(BaseModel):
    officer_id: int
    unit_id: int
    assignment_type: AssignmentTypeEnum = AssignmentTypeEnum.permanent
    start_date: date
    end_date: date | None = None


class UnitAssignmentCreate(UnitAssignmentBase):
    pass


class UnitAssignmentUpdate(BaseModel):
    end_date: date | None = None
    assignment_type: AssignmentTypeEnum | None = None


class UnitAssignmentRead(UnitAssignmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
