from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.enums import OperationParticipantRoleEnum


class OperationParticipantBase(BaseModel):
    operation_id: int
    officer_id: int
    role_in_operation: OperationParticipantRoleEnum = OperationParticipantRoleEnum.participant


class OperationParticipantCreate(OperationParticipantBase):
    pass


class OperationParticipantUpdate(BaseModel):
    role_in_operation: OperationParticipantRoleEnum | None = None


class OperationParticipantRead(OperationParticipantBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
