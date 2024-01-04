from typing import Generic, TypeVar, List, Union
from pydantic import Field
from pydantic import BaseModel

T = TypeVar("T")
DATA = TypeVar("DATA")


class ApiResponse(BaseModel, Generic[T]):
    """
    自定义返回模型
    """
    code: int = Field(default=200, description="返回码")
    message: str = Field(default="success", description="消息内容")
    data: Union[T, None] = None


class SearchResponse(BaseModel, Generic[DATA]):
    total: int
    data: List[DATA] = []
