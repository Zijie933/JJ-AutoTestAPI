import json
from json import JSONDecodeError

from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from typing import Optional, Dict, List, Any

from common.models.assertModel import Assert, AssertResult
from common.models.example import Example


class ApiTestCase(SQLModel, table=True):
    """
    APITest 基础信息模型
    """
    id: Optional[int] = Field(default=None, primary_key=True, index=True, description="用例 ID")
    name: str = Field(..., description="用例名称")
    url: str = Field(..., description="接口 URL")
    method: str = Field(..., description="请求方法")

class ApiTestResponse(SQLModel):
    """
    自定义 API 响应类
    """
    status_code: int = Field(-1, description="响应状态码")
    cookies: Dict[str, Any] = Field({}, description="响应 Cookie")
    headers: Dict[str, Any] = Field({}, description="响应 Header")
    body: Any = Field(None, description="响应 Body")

    @staticmethod
    def init(*, status_code: int = None, headers: dict = None, cookies: dict = None, text: str = None):
        try:
            body = json.loads(text)
        except JSONDecodeError or TypeError:
            body = text
        return ApiTestResponse(
            status_code=status_code,
            headers=headers,
            cookies=cookies,
            body=body
        )

    def _parse_json(self, json_str: str) -> Dict[str, Any]:
        """
        字符串解析成字典
        """
        try:
            if not json_str:
                return {}
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {}

    def get_json_response(self) -> Dict[str, Any]:
        """
        获取响应体的 JSON 数据（字典）
        """
        return self.body

    def get_header(self, key: str) -> Any:
        """
        获取响应头中的字段值
        """
        return self.headers.get(key)

    def get_cookie(self, key: str) -> Any:
        """
        获取 Cookie 中的字段值
        """
        return self.cookies.get(key)




class ApiTestCaseRunModel(BaseModel):
    """
    用例执行输入模型
    """
    case_id: Optional[int] = Field(..., description="用例 ID")
    case: Optional[ApiTestCase] = Field(None, description="用例")

    # # 断言列表
    # asserts: List[Assert] = Field(default_factory=list, description="断言列表")
    #
    # # 请求部分
    # headers: Optional[str] = Field(default=None, description="请求头")
    # params: Optional[str] = Field(default=None, description="Query 参数")
    # body: Optional[str] = Field(default=None, description="请求体")
    # cookies: Optional[str] = Field(default=None, description="请求 Cookies")
    timeout: Optional[int] = Field(default=10, description="全局请求超时时间，单位秒")

    # 用例列表
    examples: Optional[list[Example]] = Field(default=[], description="用例列表")

    # # 响应部分
    # response: Optional[ApiTestResponse] = Field(default=None, description="响应部分")


class ApiRunnerResult(SQLModel):
    """
    Runner运行结果
    """
    message: str = Field(default=None, description="运行结果说明")
    response: ApiTestResponse = Field(default=None, description="响应部分")
    assert_result: List[AssertResult] = Field(default=[], description="断言结果")









