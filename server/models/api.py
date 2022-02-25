from sqlmodel import SQLModel, Field


class Api(SQLModel, table=True):
    __tablename__ = 'sys_api'
    id: int = Field(default=None, primary_key=True)
    tags: str
    path: str
    method: str
    summary: str
