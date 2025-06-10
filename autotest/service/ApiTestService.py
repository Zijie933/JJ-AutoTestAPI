from autotest.runner.ApiTestRunner import ApiTestRunner
from autotest.schemas.api_test_schemas import ApiTestCaseRunResponse
from common.models.api_test import ApiTestCase, ApiTestCaseRunModel


class ApiTestService:

    # 初始化数据
    @staticmethod
    def init(case: ApiTestCase) -> ApiTestCaseRunModel:
        return ApiTestCaseRunModel(
            case_id=case.id,
            case=case,
            url=case.url,
            method=case.method,
        )

    @staticmethod
    async def run(case: ApiTestCaseRunModel):
        runner = ApiTestRunner(case)
        assert_results = await runner.run_concurrent_tests()
        return ApiTestCaseRunResponse(
            id=case.case_id,
            name=case.case.name,
            url=case.case.url,
            method=case.case.method,
            running_results=assert_results,
        )




