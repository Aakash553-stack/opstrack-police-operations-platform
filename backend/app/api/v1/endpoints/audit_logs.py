from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import crud_audit_log
from app.db.session import get_db
from app.schemas.audit_log import AuditLogRead

# Audit logs are append-only and written internally by the application, not
# through the public API, so this router is intentionally read-only.
router = APIRouter()


@router.get("/", response_model=list[AuditLogRead])
def list_audit_logs(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[AuditLogRead]:
    return crud_audit_log.get_multi(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=AuditLogRead)
def get_audit_log(item_id: int, db: Session = Depends(get_db)) -> AuditLogRead:
    obj = crud_audit_log.get(db, item_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Audit log entry not found")
    return obj
