from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from common.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")

# 数据库会话对象
SessionDep = Annotated[Session, Depends(get_db)]

