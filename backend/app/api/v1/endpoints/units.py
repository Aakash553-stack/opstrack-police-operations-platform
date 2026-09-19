from app.api.v1.router_factory import build_crud_router
from app.crud import crud_unit
from app.schemas.unit import UnitCreate, UnitRead, UnitUpdate

router = build_crud_router(
    crud=crud_unit,
    schema_read=UnitRead,
    schema_create=UnitCreate,
    schema_update=UnitUpdate,
    resource_name="Unit",
)
