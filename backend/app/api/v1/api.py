from fastapi import APIRouter

from app.api.v1.endpoints import (
    audit_logs,
    incidents,
    officers,
    operation_participants,
    operations,
    patrols,
    promotions,
    ranks,
    training_attendance,
    training_sessions,
    unit_assignments,
    units,
    users,
)

api_router = APIRouter()

api_router.include_router(ranks.router, prefix="/ranks", tags=["ranks"])
api_router.include_router(units.router, prefix="/units", tags=["units"])
api_router.include_router(officers.router, prefix="/officers", tags=["officers"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(promotions.router, prefix="/promotions", tags=["promotions"])
api_router.include_router(
    unit_assignments.router, prefix="/unit-assignments", tags=["unit-assignments"]
)
api_router.include_router(operations.router, prefix="/operations", tags=["operations"])
api_router.include_router(
    operation_participants.router,
    prefix="/operation-participants",
    tags=["operation-participants"],
)
api_router.include_router(patrols.router, prefix="/patrols", tags=["patrols"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(
    training_sessions.router, prefix="/training-sessions", tags=["training-sessions"]
)
api_router.include_router(
    training_attendance.router, prefix="/training-attendance", tags=["training-attendance"]
)
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])
