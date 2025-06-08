import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, index=True, primary_key=True)
    username: str = Field(index=True, unique=True, min_length=1, max_length=12, description="用户名")
    password: str | None = None
    name: str | None = Field(None, min_length=1, max_length=12, description="昵称")
    email: EmailStr | None = Field(None, description="邮箱")

    create_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))