from app.api.v1.router_factory import build_crud_router
from app.crud import crud_rank
from app.schemas.rank import RankCreate, RankRead, RankUpdate

router = build_crud_router(
    crud=crud_rank,
    schema_read=RankRead,
    schema_create=RankCreate,
    schema_update=RankUpdate,
    resource_name="Rank",
)
