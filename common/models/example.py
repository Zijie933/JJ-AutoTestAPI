from typing import Optional, List

from sqlmodel import SQLModel, Field

from common.models.assertModel import Assert, AssertResult


class Example(SQLModel):
    """
    用例参数
    """
    headers: Optional[str] = Field(default=None, description="请求头")
    params: Optional[str] = Field(default=None, description="Query 参数")
    body: Optional[str] = Field(default=None, description="请求体")
    cookies: Optional[str] = Field(default=None, description="请求 Cookies")
    timeout: Optional[int] = Field(default=None, description="局部请求超时时间，单位秒")

    asserts: Optional[List[Assert]] = Field(default=[], description="断言")
