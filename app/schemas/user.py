import uuid
from datetime import datetime

from pydantic import Field, EmailStr
from sqlmodel import SQLModel


class UserBase(SQLModel):
    username: str = Field(..., min_length=1, max_length=12)

class UserCreate(UserBase):
    password: str = Field("123456", min_length=6, max_length=22)

class UserLogin(UserBase):
    password: str = Field(..., min_length=6, max_length=22)

class UserOut(UserBase):
    id: uuid.UUID
    name: str | None
    email: EmailStr | None
    create_time: datetime

class UserUpdate(UserBase):
    name: str | None
    email: EmailStr | None
    password: str | None = Field(None, min_length=6, max_length=22)

