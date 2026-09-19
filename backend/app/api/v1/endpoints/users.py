from app.api.v1.router_factory import build_crud_router
from app.crud import crud_user
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = build_crud_router(
    crud=crud_user,
    schema_read=UserRead,
    schema_create=UserCreate,
    schema_update=UserUpdate,
    resource_name="User",
)
