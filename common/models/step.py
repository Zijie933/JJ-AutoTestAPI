from typing import Optional, List, Dict

from pydantic import Field, BaseModel
from sqlmodel import SQLModel

from common.models.api_test import ApiTestCase, ApiTestResponse
from common.models.assertModel import Assert, AssertResult
from common.models.example import Example


class Step(SQLModel):
    name: Optional[str] = Field(default=None, description="步骤名称")
    case: Optional[ApiTestCase] = Field(default=None, description="请求Case")
    asserts: Optional[List[Assert]] = Field(default=[], description="断言")
    extract: Optional[Dict] = Field(default={}, description="提取变量")

class StepRunModel(BaseModel):
    """
    用例步骤执行输入模型
    """
    case_id: Optional[int] = Field(None, description="用例 ID")
    case: Optional[ApiTestCase] = Field(None, description="用例")
    timeout: Optional[int] = Field(default=10, description="全局请求超时时间，单位秒")
    examples: Optional[list[Example]] = Field(default=[], description="用例列表")

    steps: Optional[list[Step]] = Field(default=[], description="用例步骤列表")
    env: Optional[Dict] = Field(default={}, description="环境变量")

class SingleStepRunnerResult(SQLModel):
    """
    单个 Step 运行结果
    """
    success: bool = Field(default=None, description="运行结果")
    message: str = Field(default=None, description="运行结果说明")
    response: ApiTestResponse = Field(default=None, description="响应部分")
    assert_result: List[AssertResult] = Field(default=[], description="用例结果")

class StepRunnerResult(SQLModel):
    """
    StepRunner 运行结果
    """
    success: bool = Field(default=False, description="运行结果")
    message: str = Field(default=None, description="运行结果说明")
    step_result: List[SingleStepRunnerResult] = Field(default=[], description="步骤结果")
    end_env: Optional[Dict] = Field(default={}, description="最终环境变量")
