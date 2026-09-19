from app.api.v1.router_factory import build_crud_router
from app.crud import crud_operation
from app.schemas.operation import OperationCreate, OperationRead, OperationUpdate

router = build_crud_router(
    crud=crud_operation,
    schema_read=OperationRead,
    schema_create=OperationCreate,
    schema_update=OperationUpdate,
    resource_name="Operation",
)
