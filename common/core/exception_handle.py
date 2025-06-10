from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY

from common.core.constants import ErrorMessages
from common.core.exceptions import AppBaseException
from common.schemas.response import Response


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(AppBaseException)
    async def app_base_exception_handler(request: Request, exc: AppBaseException):
        logger.error(f"捕获 AppBaseException 异常:{exc}")
        return Response.fail(message=exc.message, code=exc.code, data=None).to_json_response()

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"捕获 RequestValidationError 异常:{exc}")
        return Response.fail(
            message=ErrorMessages.PARAM_ERROR,
            code=HTTP_422_UNPROCESSABLE_ENTITY,
            data=None
        ).to_json_response()

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"捕获 Exception 异常:{exc}")
        return Response.fail(
            message=ErrorMessages.SERVER_ERROR,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            data=None
        ).to_json_response()
