from typing import Generic, Optional, TypeVar, Any

from loguru import logger
from pydantic.generics import GenericModel
from fastapi.responses import JSONResponse

T = TypeVar("T")

class Response(GenericModel, Generic[T]):
    code: int
    message: str
    data: Optional[T] = None

    @staticmethod
    def success(data: T | None = None, message: str = "success") -> "Response[T]":
        return Response[T](code=0, message=message, data=data)

    @staticmethod
    def fail(*, message: str = "fail", code: int = -1, data: Any | None = None) -> "Response[Any]":
        return Response[Any](code=code, message=message, data=data)

    def to_json_response(self, status_code: int = 200) -> JSONResponse:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=status_code, content=self.dict())
