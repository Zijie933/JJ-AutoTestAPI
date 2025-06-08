import uuid

from sqlalchemy.orm import Session

from common.core.security import get_password_hash
from common.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(*, db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def create_user(*, db: Session, user_in: UserCreate):
    db_user = User.model_validate(
        user_in, update={"password": get_password_hash(user_in.password)}
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(*, db: Session, user_in: UserUpdate):
    db_user = db.query(User).filter(User.id == user_in.id).first()
    if not db_user:
        return None

    if user_in.username is not None:
        db_user.username = user_in.username
    if user_in.email is not None:
        db_user.email = user_in.email
    if user_in.password is not None:
        db_user.password = get_password_hash(user_in.password)
    if user_in.is_active is not None:
        db_user.is_active = user_in.is_active

    db.commit()
    db.refresh(db_user)
    return db_user



