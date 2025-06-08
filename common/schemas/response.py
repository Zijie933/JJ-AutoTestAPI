from typing import Generic, Optional, TypeVar, Any
from pydantic.generics import GenericModel

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
