from app.api.v1.router_factory import build_crud_router
from app.crud import crud_promotion
from app.schemas.promotion import PromotionCreate, PromotionRead, PromotionUpdate

router = build_crud_router(
    crud=crud_promotion,
    schema_read=PromotionRead,
    schema_create=PromotionCreate,
    schema_update=PromotionUpdate,
    resource_name="Promotion",
)
