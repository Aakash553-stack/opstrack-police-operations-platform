from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.enums import AuditActionEnum


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    action: AuditActionEnum
    table_name: str
    record_id: int | None = None
    old_values: dict[str, Any] | None = None
    new_values: dict[str, Any] | None = None
    ip_address: str | None = None
    created_at: datetime
