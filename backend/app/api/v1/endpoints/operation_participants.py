from app.api.v1.router_factory import build_crud_router
from app.crud import crud_operation_participant
from app.schemas.operation_participant import (
    OperationParticipantCreate,
    OperationParticipantRead,
    OperationParticipantUpdate,
)

router = build_crud_router(
    crud=crud_operation_participant,
    schema_read=OperationParticipantRead,
    schema_create=OperationParticipantCreate,
    schema_update=OperationParticipantUpdate,
    resource_name="Operation participant",
)
