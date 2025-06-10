import asyncio
import json
from typing import List

import httpx
from httpx import Response, TimeoutException, RequestError, Request
from loguru import logger
from sqlmodel import Session

from autotest.deps import SessionDep
from autotest.runner.AssertRunner import AssertRunner
from common.models.api_test import ApiTestCaseRunModel, ApiTestCase, ApiTestResponse, ApiRunnerResult
from common.models.assertModel import AssertResult, Assert, AssertCategory, AssertOperator
from common.models.example import Example


class ApiTestRunner:

    def __init__(self, run_model: ApiTestCaseRunModel, max_concurrency: int = 10):
        self.run_model = run_model
        self.max_concurrency = max_concurrency

    async def run_concurrent_tests(self) -> List[ApiRunnerResult]:
        """
        并发请求
        :return:
        """
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def limited_task(client: httpx.AsyncClient, example: Example):
            async with semaphore:
                return await self.run_single_test(client, example)

        async with httpx.AsyncClient(
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
                timeout=self.run_model.timeout
        ) as client:
            tasks = [limited_task(client, example) for example in self.run_model.examples or [Example()]]
            return await asyncio.gather(*tasks)

    async def run_single_test(self, client: httpx.AsyncClient, example: Example) -> ApiRunnerResult:
        """
        运行单个请求
        :param client:
        :param example:
        :param run_model:
        :return:
        """
        result = ApiRunnerResult()

        try:
            request_obj = client.build_request(
                url=self.run_model.case.url,
                method=self.run_model.case.method.upper(),
                cookies=json.loads(example.cookies) if example.cookies else {},
                headers=json.loads(example.headers) if example.headers else {},
                params=json.loads(example.params) if example.params else {},
                data=example.body,
                timeout=example.timeout if example.timeout else self.run_model.timeout
            )
            response_obj: Response = await client.send(request_obj)

            # 将响应封装成 ApiTestResponse
            response_time_ms = response_obj.elapsed.total_seconds() * 1000
            result.response = ApiTestResponse.init(
                status_code=response_obj.status_code,
                body=response_obj.content.__str__(),
                cookies=response_obj.cookies,
                headers=response_obj.headers,
            )

            for assertion in example.asserts:
                res = AssertRunner.run_assert(assertion, result.response, response_time=response_time_ms)
                result.assert_result.append(AssertResult(
                    message=res.message,
                    success=res.success
                ))

            # 假如没有断言
            if not result.assert_result:
                result.assert_result.append(AssertResult(message="未设定断言", success=True))

        except Exception as e:
            result.message = f"请求失败: {str(e)}"

        return result

    async def run_test(self) -> List[ApiRunnerResult]:
        """
        执行 API 测试用例 --- 无并发
        """
        run_model = self.run_model
        case = run_model.case
        url = case.url if case else None
        method = case.method.upper() if case else None
        if not url:
            return [ApiRunnerResult(message="用例对应的URL不存在")]
        if not method:
            return [ApiRunnerResult(message="用例对应的请求方法不存在")]
        timeout = run_model.timeout or 10
        if method.upper() not in ["GET", "POST", "PUT", "DELETE"]:
            raise ValueError(f"不支持的请求方法: {method}")

        # 发起 HTTP 请求
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if not run_model.examples:
                    run_model.examples.append(Example())

                results = []
                for example in run_model.examples:
                    result = await self.run_single_test(client, example)
                    results.append(result)

                return results

        except TimeoutException as e:
            return [ApiRunnerResult(message=f"run请求超时: {str(e)}")]

        except RequestError as e:
            return [ApiRunnerResult(message=f"run请求失败: {str(e)}")]

        except Exception as e:
            return [ApiRunnerResult(message=f"run执行异常: {str(e)}")]
