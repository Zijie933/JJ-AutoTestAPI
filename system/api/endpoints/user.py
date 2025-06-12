import uuid
from datetime import timedelta

from fastapi import APIRouter

from system.deps import SessionDep
from common.core import security
from common.core.PayloadLocal import payloadLocal
from common.core.config import settings
from common.core.exceptions import UsernameAlreadyExistsException, UsernameNotExistsException, \
    PasswordIncorrectException, TokenInvalidException
from common.schemas.response import Response
from system.schemas.user_schemas import UserCreate, UserOut, UserLogin, UserUpdate
from system.crud import user_crud

router = APIRouter()

@router.post("/register", response_model=Response, description="新建用户")
async def create_user(*, db: SessionDep, user_in: UserCreate):
    """
    新建用户
    :param db:
    :param user_in:
    :return:
    """
    user = user_crud.get_user_by_username(username=user_in.username, db=db)
    if user:
        raise UsernameAlreadyExistsException()

    user = user_crud.create_user(user=user_in, db=db)
    return Response.success(data=user)


@router.get("/", response_model=Response[UserOut], description="获取用户信息")
async def get_user(*, db: SessionDep):
    """
    获取用户信息
    :param db:
    :return:
    """
    payload = payloadLocal.payload
    if not payload:
        raise TokenInvalidException()
    user_id = uuid.UUID(payload.get("sub"))
    user = user_crud.get_user_by_id(user_id=user_id, db=db)
    return Response.success(data=user)


@router.post("/login", response_model=Response[str], description="用户登录")
async def login(*, db: SessionDep, user_in: UserLogin):
    """
    用户登录
    :param db:
    :param user_in:
    :return:
    """
    user = user_crud.get_user_by_username(username=user_in.username, db=db)

    if not user:
        raise UsernameNotExistsException()

    if not security.verify_password(password=user_in.password, hashed_password=user.password):
        raise PasswordIncorrectException()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_jwt_token(user_id=user.id, expires_delta=access_token_expires)

    return Response.success(data=token, message="登录成功")

# 更新用户信息
@router.put("/", response_model=Response)
def update_user(*, db: SessionDep, user_in: UserUpdate):
    """
    更新用户信息
    :param db:
    :param user_in:
    :return:
    """
    user = user_crud.update_user(db=db, user_in=user_in)
    if not user:
        raise UsernameNotExistsException()
    return Response.success()



