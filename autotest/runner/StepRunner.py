import asyncio
import re
import json
from typing import List, Dict, Optional, Any

from httpx import Response
from loguru import logger
from tblib.decorators import return_error

from autotest.runner.AssertRunner import AssertRunner
from common.core.exceptions import StepRunError
from common.models.api_test import ApiTestCaseRunModel, ApiTestResponse, ApiRunnerResult, ApiTestCase
from common.models.step import Step, SingleStepRunnerResult, StepRunnerResult
from common.models.example import Example
from common.models.assertModel import AssertResult
from autotest.runner.ApiTestRunner import ApiTestRunner
from common.utils.replace_env import replace_vars_in_case


class StepRunner:
    def __init__(self, steps: List[Step] = None, env: Optional[Dict[str, Any]] = None, max_concurrency: int = 10):
        self.env = env or {}
        self.steps = steps or []
        self.max_concurrency = max_concurrency

    async def run(self) -> StepRunnerResult:
        """
        启动整个流程
        :return: 最终 env
        """
        if not self.steps:
            return StepRunnerResult(message="无测试步骤", success=True, end_env=self.env)

        logger.info("开始执行测试步骤")
        res, success = await self.run_steps(self.steps)
        if not success:
            return StepRunnerResult(message="测试步骤执行失败", success=False, end_env=self.env, step_result=res)
        logger.info("测试步骤执行完成，最终环境变量: {}", self.env)
        return StepRunnerResult(message="测试步骤执行成功", success=True, end_env=self.env, step_result=res)

    async def run_steps(self, steps: List[Step]) -> (List[SingleStepRunnerResult], bool):
        """
        执行一组步骤，并共享 env 环境变量
        :param steps: 步骤列表
        :param env: 初始环境变量
        :return: 更新后的 env
        """
        current_env = self.env.copy()
        res = []
        for step in steps:
            logger.info(f"正在执行步骤: {step.name}")
            updated_step = self._replace_step_vars(step, current_env)
            result = await self._run_single_step(updated_step)
            if result.success:
                extracted = self._extract_vars(result.response, step.extract)
                current_env.update(extracted)
                res.append(result)
            else:
                return res, False
        self.env = current_env
        return res, True

    def _replace_step_vars(self, step: Step, env: Dict[str, Any]) -> Step:
        if not step.case:
            return step

        new_case = replace_vars_in_case(step.case, env)
        return step.model_copy(update={"case": new_case})

    async def _run_single_step(self, step: Step) -> SingleStepRunnerResult:
        """
        执行单个步骤，并根据 asserts 判断是否提取变量
        """
        if not step.case:
            return SingleStepRunnerResult(success=False, message="缺少请求参数")

        run_model = ApiTestCaseRunModel(case=step.case)
        runner = ApiTestRunner(run_model)
        results = await runner.run_test()
        result: ApiRunnerResult = results[0]
        step_result = SingleStepRunnerResult()

        # 如果存在 asserts，则执行断言判断
        assert_result = []
        if step.asserts and result.response:
            for assert_ in step.asserts:
                assert_result.append(AssertRunner.run_assert(assertion=assert_, response=result.response, env=self.env))
            step_result.response = result.response
            step_result.assert_result = assert_result

            # 如果有任何断言失败，就不提取 extract 变量
            if any(not a.success for a in assert_result):
                step_result.message = "断言失败"
                step_result.success = False
                return step_result

        step_result.success = True
        return step_result

    def _extract_vars(self, response: ApiTestResponse, extract_rules: Dict[str, str]) -> Dict[str, Any]:
        """
        根据 extract 规则从 response 中提取变量
        """
        extracted = {}

        for var_name, path in extract_rules.items():
            parts = path.split('.')
            if not parts:
                continue

            source = parts[0]
            key_path = parts[1:]

            try:
                if source == 'body':
                    try:
                        current = json.dumps(response.body, ensure_ascii=False) if response.body else {}
                    except json.JSONDecodeError:
                        return extracted
                elif source == 'headers':
                    current = dict(response.headers)
                elif source == 'cookies':
                    current = dict(response.cookies)
                else:
                    continue

                for part in key_path:
                    current = current.get(part) if isinstance(current, dict) else getattr(current, part, None)
                    if current is None:
                        break

                if current is not None:
                    extracted[var_name] = current

            except Exception as e:
                logger.error(f"提取失败: {var_name} - {e}")
                continue

        return extracted
