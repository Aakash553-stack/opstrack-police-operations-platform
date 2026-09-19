from app.api.v1.router_factory import build_crud_router
from app.crud import crud_officer
from app.schemas.officer import OfficerCreate, OfficerRead, OfficerUpdate

router = build_crud_router(
    crud=crud_officer,
    schema_read=OfficerRead,
    schema_create=OfficerCreate,
    schema_update=OfficerUpdate,
    resource_name="Officer",
)
