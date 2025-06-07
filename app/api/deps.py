from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

# 数据库会话对象
SessionDep = Annotated[Session, Depends(get_db)]