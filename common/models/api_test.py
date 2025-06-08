import json

from mypy.stubtest import test_stubs
from sqlmodel import SQLModel, Field
from typing import Optional, Dict, List, Any

from common.models.assertModel import Assert


class ApiTestCase(SQLModel, table=True):
    """
    APITest 基础信息模型
    """
    id: Optional[int] = Field(default=None, primary_key=True, index=True, description="用例 ID")
    name: str = Field(..., description="用例名称")
    url: str = Field(..., description="接口 URL")

class ApiTestResponse:
    """
    自定义 API 响应类
    """
    def __init__(self, status_code: int, headers: str, cookies: str, text: str):
        self.status_code = status_code
        self.text = text

        self.headers = self._parse_json(headers)
        self.cookies = self._parse_json(cookies)

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
        try:
            return json.loads(self.text)
        except json.JSONDecodeError:
            return {}

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




class ApiTestCaseRunModel:
    """
    用例执行输入模型
    """
    case_id: Optional[int] = Field(..., description="用例 ID")

    # 断言列表
    asserts: List[Assert] = Field(default_factory=list, description="断言列表")

    # 请求部分
    method: str = Field(..., description="请求方法（GET/POST/PUT/DELETE）")
    headers: Optional[str] = Field(default=None, description="请求头")
    params: Optional[str] = Field(default=None, description="Query 参数")
    body: Optional[str] = Field(default=None, description="请求体")
    cookies: Optional[str] = Field(default=None, description="请求 Cookies")
    timeout: Optional[int] = Field(default=10, description="请求超时时间，单位秒")

    # 响应部分
    response: ApiTestResponse


    









