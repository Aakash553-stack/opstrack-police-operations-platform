from app.api.v1.router_factory import build_crud_router
from app.crud import crud_patrol
from app.schemas.patrol import PatrolCreate, PatrolRead, PatrolUpdate

router = build_crud_router(
    crud=crud_patrol,
    schema_read=PatrolRead,
    schema_create=PatrolCreate,
    schema_update=PatrolUpdate,
    resource_name="Patrol",
)
