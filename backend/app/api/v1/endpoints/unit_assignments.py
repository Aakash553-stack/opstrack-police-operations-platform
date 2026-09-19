from app.api.v1.router_factory import build_crud_router
from app.crud import crud_unit_assignment
from app.schemas.unit_assignment import (
    UnitAssignmentCreate,
    UnitAssignmentRead,
    UnitAssignmentUpdate,
)

router = build_crud_router(
    crud=crud_unit_assignment,
    schema_read=UnitAssignmentRead,
    schema_create=UnitAssignmentCreate,
    schema_update=UnitAssignmentUpdate,
    resource_name="Unit assignment",
)
