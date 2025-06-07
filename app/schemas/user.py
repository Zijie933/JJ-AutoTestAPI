from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    # user_id: Optional[str]
    username: str = Field(..., min_length=1, max_length=12, description="用户名")
    password: Optional[str] = Field("123456", min_length=6, max_length=18, description="密码")
    email: Optional[EmailStr] = Field(None, description="邮箱")

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True
