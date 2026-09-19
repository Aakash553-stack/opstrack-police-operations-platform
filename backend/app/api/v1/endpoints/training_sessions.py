from app.api.v1.router_factory import build_crud_router
from app.crud import crud_training_session
from app.schemas.training_session import (
    TrainingSessionCreate,
    TrainingSessionRead,
    TrainingSessionUpdate,
)

router = build_crud_router(
    crud=crud_training_session,
    schema_read=TrainingSessionRead,
    schema_create=TrainingSessionCreate,
    schema_update=TrainingSessionUpdate,
    resource_name="Training session",
)
