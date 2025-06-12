from typing import Optional, List, AnyStr, Any, Dict

from doc.pycurl.examples.quickstart.response_headers import headers
from pydantic import Field
from sqlmodel import SQLModel

from autotest.schemas.examples import apiTestCaseRunParamsExample
from common.models.api_test import ApiTestResponse, ApiTestCase
from common.models.assertModel import Assert, AssertCategory, AssertOperator
from common.models.example import Example
from common.models.step import Step, SingleStepRunnerResult


class ApiTestCaseCreate(SQLModel):
    name: str = Field(..., description="用例名称", examples=["测试用例1"])
    url: str = Field(..., description="接口请求地址", examples=["http://www.baidu.com"])
    method: str = Field(..., description="请求方法，如GET、POST", examples=["GET"])

class ApiTestCaseUpdate(SQLModel):
    id: int = Field(..., description="用例 ID", examples=[1])
    name: Optional[str] = Field(default=None, description="用例名称", examples=["测试用例2"])
    url: Optional[str] = Field(default=None, description="接口请求地址", examples=["http://www.baidu.com"])
    method: Optional[str] = Field(default=None, description="请求方法，如GET、POST", examples=["GET"])

class ApiTestCaseRunParams(SQLModel):
    id: Optional[int] = Field(default=None, description="用例 ID", examples=apiTestCaseRunParamsExample.get("id"))
    case: Optional[ApiTestCase] = Field(default=None, description="快捷用例", examples=apiTestCaseRunParamsExample.get("case"))
    examples: Optional[list[Example]] = Field(default=[], description="测试变量", examples=apiTestCaseRunParamsExample.get("examples"))

class StepInput(SQLModel):
    name: Optional[str] = Field(default=None, description="步骤名称")
    case: Optional[ApiTestCase] = Field(default=None, description="请求参数")
    asserts: Optional[list[Assert]] = Field(default=[], description="断言")
    extract: Optional[str] = Field(default=None, description="提取参数(JSON)")

class ApiTestStepsRunParams(SQLModel):
    id: Optional[int] = Field(default=None, description="用例 ID", examples=apiTestCaseRunParamsExample.get("id"))
    case: Optional[ApiTestCase] = Field(default=None, description="快捷用例", examples=apiTestCaseRunParamsExample.get("case"))
    examples: Optional[list[Example]] = Field(default=[], description="测试变量", examples=apiTestCaseRunParamsExample.get("examples"))

    steps: Optional[list[StepInput]] = Field(default=[], description="步骤", examples=apiTestCaseRunParamsExample.get("steps"))
    env: Optional[str] = Field(default=None, description="环境变量(JSON)", examples=apiTestCaseRunParamsExample.get("env"))

class ApiTestCaseRunResponse(SQLModel):
    # id: Optional[int] = Field(default=None, description="用例 ID")
    # name: str = Field(..., description="用例名称")
    # url: str = Field(..., description="接口 URL")
    # method: str = Field(..., description="请求方法")
    case: Optional[ApiTestCase] = Field(default=None, description="用例")
    # 运行结果
    running_results: List[Any]

class StepRunResponse(SQLModel):
    case: Optional[ApiTestCase] = Field(default=None, description="用例")
    running_results: List[Any]

    step_run_success: bool = Field(default=False, description="运行结果")
    step_run_message: str = Field(default=None, description="运行结果说明")
    step_run_result: List[SingleStepRunnerResult] = Field(default=[], description="步骤结果")
    end_env: Optional[Dict] = Field(default={}, description="最终环境变量")
