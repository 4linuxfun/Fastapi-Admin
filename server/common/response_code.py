from typing import Generic, TypeVar, Optional, List
from pydantic import Field
from pydantic.generics import GenericModel

T = TypeVar("T")
DATA = TypeVar("DATA")


class ApiResponse(GenericModel, Generic[T]):
    """
    自定义返回模型
    """
    code: int = Field(default=200, description="返回码")
    message: str = Field(default="success", description="消息内容")
    data: Optional[T]


class SearchResponse(GenericModel, Generic[DATA]):
    total: int
    data: List[DATA] = []
