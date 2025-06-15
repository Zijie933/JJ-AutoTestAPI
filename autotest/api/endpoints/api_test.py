from typing import List, Optional

from fastapi import APIRouter
from loguru import logger
from pydantic import ValidationError

from autotest.crud import api_test_crud
from autotest.schemas.api_test_schemas import ApiTestCaseCreate, ApiTestCaseUpdate, ApiTestCaseRunParams, \
    ApiTestStepsRunParams
from autotest.service.ApiTestService import ApiTestService
from common.core.constants import ErrorMessages
from common.core.exceptions import MissingFieldException
from common.models.api_test import ApiTestCase
from system.deps import SessionDep
from common.schemas.response import Response

router = APIRouter()

valid_methods = {"GET", "POST", "PUT", "DELETE"}

# 上传测试接口
@router.post("/create", response_model=Response, description="上传测试接口")
async def create_api_test(*, db: SessionDep, test_in: ApiTestCaseCreate):
    method_upper = test_in.method.upper()
    if method_upper not in valid_methods:
        return Response.fail(message=ErrorMessages.METHOD_NOT_ALLOWED)

    api_test_case = api_test_crud.save_api_test(db=db, test_in=test_in)
    if not api_test_case:
        return Response.fail(message=ErrorMessages.TEST_SAVE_FAILED)

    return Response.success(data=api_test_case)

@router.put("/update", response_model=Response, description="更新测试接口")
async def update_api_test(*, db: SessionDep, test_in: ApiTestCaseUpdate):
    if test_in.method is not None:
        method_upper = test_in.method.upper()
        if method_upper not in valid_methods:
            return Response.fail(message=ErrorMessages.METHOD_NOT_ALLOWED)
        test_in.method = method_upper

    api_test_case = api_test_crud.update_api_test(db=db, test_in=test_in)
    if not api_test_case:
        return Response.fail(message=ErrorMessages.TEST_NOT_EXIST)

    return Response.success(data=api_test_case)

@router.get("/list", response_model=Response, description="获取接口列表")
def get_api_test_list(db: SessionDep):
    api_test_cases = api_test_crud.get_api_test_list(db=db)
    return Response.success(data=api_test_cases)

@router.get("/{case_id}", response_model=Response, description="根据id获取接口")
def get_api_test_by_id(*, db: SessionDep, case_id: int):
    api_test_case = api_test_crud.get_api_test_by_id(db=db, test_id=case_id)
    if not api_test_case:
        return Response.fail(message=ErrorMessages.TEST_NOT_EXIST)

    return Response.success(data=api_test_case)

@router.post("/run", response_model=Response, description="测试id接口")
async def run_api_test(*, db: SessionDep, test_in: ApiTestCaseRunParams):
    case_run_model = ApiTestService.init_case(db=db, run_params=test_in)
    response = await ApiTestService.run_case(case_run_model)
    logger.info(response)
    return Response.success(data=response)


@router.post("/steps/run", response_model=Response, description="测试多依赖接口")
async def run_api_test(*, db: SessionDep, test_in: ApiTestStepsRunParams):
    step_run_model = ApiTestService.init_step(db=db, run_params=test_in)
    response = await ApiTestService.run_steps(step_run_model)
    return Response.success(data=response)

@router.delete("/{case_id}", response_model=Response, description="删除接口")
def delete_api_test(*, db: SessionDep, case_id: int):
    result = api_test_crud.delete_api_test(db=db, test_id=case_id)
    if not result:
        return Response.fail(message=ErrorMessages.TEST_NOT_EXIST)

    return Response.success()

