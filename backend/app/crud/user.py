from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def create(self, db: Session, obj_in: UserCreate) -> User:
        data = obj_in.model_dump(exclude={"password"})
        db_obj = User(**data, password_hash=get_password_hash(obj_in.password))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: User, obj_in: UserUpdate) -> User:
        data = obj_in.model_dump(exclude_unset=True, exclude={"password"})
        for field, value in data.items():
            setattr(db_obj, field, value)
        if obj_in.password is not None:
            db_obj.password_hash = get_password_hash(obj_in.password)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


crud_user = CRUDUser(User)
