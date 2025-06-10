from typing import Optional, List, AnyStr, Any

from doc.pycurl.examples.quickstart.response_headers import headers
from pydantic import Field
from sqlmodel import SQLModel

from common.models.api_test import ApiTestResponse
from common.models.assertModel import Assert, AssertCategory, AssertOperator
from common.models.example import Example


class ApiTestCaseCreate(SQLModel):
    name: str = Field(..., description="用例名称", examples=["测试用例1"])
    url: str = Field(..., description="接口请求地址", examples=["http://www.baidu.com"])
    method: str = Field(..., description="请求方法，如GET、POST", examples=["GET"])

class ApiTestCaseUpdate(SQLModel):
    id: int = Field(..., description="用例 ID", examples=[1])
    name: Optional[str] = Field(default=None, description="用例名称", examples=["测试用例2"])
    url: Optional[str] = Field(default=None, description="接口请求地址", examples=["http://www.baidu.com"])
    method: Optional[str] = Field(default=None, description="请求方法，如GET、POST", examples=["GET"])

class ApiTestCaseRunModel(SQLModel):
    id: int = Field(..., description="用例 ID")
    asserts: list[Assert] = Field(default=[], description="断言")

class ApiTestCaseRunParams(SQLModel):
    id: Optional[int] = Field(default=None, description="用例 ID", examples=[1])
    examples: Optional[list[Example]] = Field(default=[], description="用例", examples=[[
        Example(
            headers='{"Content-Type": "application/json"}',
            asserts=[
                Assert(
                    category=AssertCategory.STATUS_CODE,
                    operator=AssertOperator.EQ,
                    expected=200
                ),
                Assert(
                    category=AssertCategory.HEADER_FIELD,
                    operator=AssertOperator.EQ,
                    path="content-type",
                    expected="application/json",
                ),
                Assert(
                    category=AssertCategory.BODY_FIELD,
                    operator=AssertOperator.EQ,
                    path="data.id",
                    expected=1,
                ),
            ]
        ),
        Example(
            headers='{"Content-Type": "application/json"}',
            asserts=[
                Assert(
                    category=AssertCategory.STATUS_CODE,
                    operator=AssertOperator.GT,
                    expected=400
                ),
                Assert(
                    category=AssertCategory.COOKIES_FIELD,
                    operator=AssertOperator.NOT_EXISTS,
                    path="BAIDUID",
                ),
                Assert(
                    category=AssertCategory.HEADER_FIELD,
                    operator=AssertOperator.CONTAINS,
                    path="x-ua-compatible",
                    expected="Edge",
                ),
            ]
        ),
    ]])

class ApiTestCaseRunResponse(SQLModel):
    id: Optional[int] = Field(default=None, description="用例 ID")
    name: str = Field(..., description="用例名称")
    url: str = Field(..., description="接口 URL")
    method: str = Field(..., description="请求方法")
    # asserts: List[Assert] = Field(default_factory=list, description="断言列表")

    # headers: Optional[str] = Field(default=None, description="请求头")
    # params: Optional[str] = Field(default=None, description="Query 参数")
    # body: Optional[str] = Field(default=None, description="请求体")
    # cookies: Optional[str] = Field(default=None, description="请求 Cookies")
    # timeout: Optional[int] = Field(default=10, description="请求超时时间，单位秒")

    # # 响应部分
    # response: Optional[ApiTestResponse] = Field(default=None, description="响应部分")

    # 运行结果
    running_results: List[Any]