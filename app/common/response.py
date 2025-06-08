from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

class ResponseHandler:
    @staticmethod
    def success(data: Any = None, message: str = "success") -> ResponseModel:
        return ResponseModel(
            code=200,
            message=message,
            data=data
        )

    @staticmethod
    def error(message: str = "error", code: int = 500, data: Any = None) -> ResponseModel:
        return ResponseModel(
            code=code,
            message=message,
            data=data
        )

    @staticmethod
    def failed(message: str = "failed", data: Any = None) -> ResponseModel:
        return ResponseModel(
            code=400,
            message=message,
            data=data
        )
