from typing import Generic, TypeVar, Optional
from pydantic import Field
from pydantic.generics import GenericModel

T = TypeVar("T")


class ApiResponse(GenericModel, Generic[T]):
    """
    自定义返回模型
    """
    code: int = Field(default=200, description="返回码")
    message: str = Field(default="success", description="消息内容")
    data: Optional[T]
