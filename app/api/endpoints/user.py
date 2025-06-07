from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import SessionDep
from app.core.exceptions import UsernameAlreadyExistsException
from app.schemas.user import UserCreate, UserOut
from app.crud import user as user_crud

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(*, db: SessionDep, user_in: UserCreate):
    """
    新建用户
    :param db:
    :param user_in:
    :return:
    """
    try:
        user = user_crud.get_user_by_username(username=user_in.username, db=db)
        if user:
            raise UsernameAlreadyExistsException(user_in.username)

        user = user_crud.create_user(user=user_in, db=db)

        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
