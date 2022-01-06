from typing import Any
from sqlmodel import SQLModel


class ApiResponse(SQLModel):
    code: int
    message: str
    data: Any