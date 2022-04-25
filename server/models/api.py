from sqlmodel import SQLModel, Field


class ApiBase(SQLModel):
    tags: str
    path: str
    method: str
    summary: str
    deprecated: int = Field(default=0)


class Api(ApiBase, table=True):
    __tablename__ = 'sys_api'
    id: int = Field(default=None, primary_key=True)
