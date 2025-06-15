import uuid
from datetime import datetime

from pydantic import Field, EmailStr, BaseModel
from sqlmodel import SQLModel


class UserBase(SQLModel):
    username: str = Field(..., min_length=1, max_length=12, examples=["Jack"])

class UserCreate(UserBase):
    password: str = Field("1234567", min_length=6, max_length=22, examples=["1234567"])

class UserLogin(UserBase):
    password: str = Field(..., min_length=6, max_length=22, examples=[{"username": "Jack", "password": "1234567"}])

class UserOut(UserBase):
    id: uuid.UUID
    name: str | None
    email: EmailStr | None
    create_time: datetime

class UserUpdate(UserBase):
    name: str | None
    email: EmailStr | None
    password: str | None = Field(None, min_length=6, max_length=22)

