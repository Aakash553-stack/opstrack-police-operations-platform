from app.api.v1.router_factory import build_crud_router
from app.crud import crud_training_attendance
from app.schemas.training_attendance import (
    TrainingAttendanceCreate,
    TrainingAttendanceRead,
    TrainingAttendanceUpdate,
)

router = build_crud_router(
    crud=crud_training_attendance,
    schema_read=TrainingAttendanceRead,
    schema_create=TrainingAttendanceCreate,
    schema_update=TrainingAttendanceUpdate,
    resource_name="Training attendance",
)
