from pydantic import ValidationError
from sqlalchemy.orm import Session

from autotest.crud import api_test_crud
from autotest.runner.ApiTestRunner import ApiTestRunner
from autotest.runner.StepRunner import StepRunner
from autotest.schemas.api_test_schemas import ApiTestCaseRunResponse, ApiTestCaseRunParams, ApiTestStepsRunParams, \
    StepRunResponse
from common.core.constants import ErrorMessages
from common.core.exceptions import MissingFieldException, StepRunError
from common.models.api_test import ApiTestCase, ApiTestCaseRunModel
from common.models.step import StepRunModel, StepRunnerResult
from common.schemas.response import Response
from common.utils.replace_env import replace_vars_in_case
from common.utils.step import convert_step_inputs_to_steps


class ApiTestService:

    # 初始化数据
    @staticmethod
    def init(*, db: Session | None, run_params: ApiTestCaseRunParams) -> ApiTestCaseRunModel:
        if not id:
            # 优选择id用例
            case = api_test_crud.get_api_test_by_id(db=db, test_id=run_params.id)
            if not case:
                return Response.fail(message=ErrorMessages.TEST_NOT_EXIST)
        else:
            try:
                case = ApiTestCase.model_validate(run_params.case)
            except ValidationError:
                raise MissingFieldException(ErrorMessages.MISSING_FIELD_MSG)
        return ApiTestCaseRunModel(
            case_id=case.id,
            case=case,
            url=case.url,
            method=case.method,
            examples=run_params.examples,
        )

    @staticmethod
    def init(*, db: Session, run_params: ApiTestStepsRunParams) -> StepRunModel:
        if not id:
            # 优选择id用例
            case = api_test_crud.get_api_test_by_id(db=db, test_id=run_params.id)
            if not case:
                return Response.fail(message=ErrorMessages.TEST_NOT_EXIST)
        else:
            try:
                case = ApiTestCase.model_validate(run_params.case)
            except ValidationError:
                raise MissingFieldException(ErrorMessages.MISSING_FIELD_MSG)
        return StepRunModel(
            case_id=case.id,
            case=case,
            url=case.url,
            method=case.method,
            examples=run_params.examples,
            steps=convert_step_inputs_to_steps(run_params.steps),
            env=run_params.env,
        )

    @staticmethod
    async def run(case: ApiTestCaseRunModel):
        runner = ApiTestRunner(case)
        assert_results = await runner.run_concurrent_tests()
        return ApiTestCaseRunResponse(
            case=case.case,
            running_results=assert_results,
        )

    @staticmethod
    async def run_steps(case: StepRunModel):
        runner = StepRunner(case.steps, case.env)
        res = await runner.run()
        if not res.success:
            return ApiTestCaseRunResponse(
            case=case.case,
            running_results=res,
        )
        case.env = res.end_env
        case.case = replace_vars_in_case(case.case, case.env)

        # 跑case
        api_run_params = ApiTestCaseRunParams(case=case.case, examples=case.examples)
        api_run_model = ApiTestService.init(db=None, run_params=api_run_params)
        api_response = await ApiTestService.run(api_run_model)

        return StepRunResponse(
            case=api_response.case,
            running_results=api_response.running_results,
            step_run_success=res.success,
            step_run_message=res.message,
            step_run_result=res.step_result,
            end_env=res.end_env
        )










