from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.session import get_db


def build_crud_router(
    *,
    crud: CRUDBase[Any, Any, Any],
    schema_read: type[BaseModel],
    schema_create: type[BaseModel],
    schema_update: type[BaseModel],
    resource_name: str,
) -> APIRouter:
    """Build a standard list/create/get/update/delete router for one resource.

    Kept generic on purpose: every table's integrity rules (uniqueness,
    valid FKs, date/format checks) are enforced by the database itself, so
    this router only needs to translate IntegrityError into a 409 — see the
    exception handler registered in app.main.
    """
    router = APIRouter()

    @router.get("/", response_model=list[schema_read])
    def list_items(
        skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
    ) -> list[Any]:
        return crud.get_multi(db, skip=skip, limit=limit)

    @router.post("/", response_model=schema_read, status_code=status.HTTP_201_CREATED)
    def create_item(obj_in: schema_create, db: Session = Depends(get_db)) -> Any:  # type: ignore[valid-type]
        return crud.create(db, obj_in)

    @router.get("/{item_id}", response_model=schema_read)
    def get_item(item_id: int, db: Session = Depends(get_db)) -> Any:
        obj = crud.get(db, item_id)
        if obj is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"{resource_name} not found")
        return obj

    @router.patch("/{item_id}", response_model=schema_read)
    def update_item(
        item_id: int, obj_in: schema_update, db: Session = Depends(get_db)  # type: ignore[valid-type]
    ) -> Any:
        obj = crud.get(db, item_id)
        if obj is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"{resource_name} not found")
        return crud.update(db, obj, obj_in)

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_item(item_id: int, db: Session = Depends(get_db)) -> None:
        obj = crud.remove(db, item_id)
        if obj is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"{resource_name} not found")

    return router
