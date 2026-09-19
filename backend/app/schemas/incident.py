from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import IncidentSeverityEnum, IncidentStatusEnum, IncidentTypeEnum


class IncidentBase(BaseModel):
    incident_number: str = Field(max_length=20)
    incident_type: IncidentTypeEnum
    severity: IncidentSeverityEnum = IncidentSeverityEnum.low
    status: IncidentStatusEnum = IncidentStatusEnum.reported
    location_description: str = Field(max_length=200)
    reporting_officer_id: int
    assigned_unit_id: int | None = None
    operation_id: int | None = None
    description: str | None = None


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    severity: IncidentSeverityEnum | None = None
    status: IncidentStatusEnum | None = None
    assigned_unit_id: int | None = None
    description: str | None = None


class IncidentRead(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reported_date: datetime
    created_at: datetime
    updated_at: datetime
