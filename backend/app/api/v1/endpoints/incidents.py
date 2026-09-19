from app.api.v1.router_factory import build_crud_router
from app.crud import crud_incident
from app.schemas.incident import IncidentCreate, IncidentRead, IncidentUpdate

router = build_crud_router(
    crud=crud_incident,
    schema_read=IncidentRead,
    schema_create=IncidentCreate,
    schema_update=IncidentUpdate,
    resource_name="Incident",
)
