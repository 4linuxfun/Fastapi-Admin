from typing import Optional
from sqlmodel import SQLModel
from datetime import datetime


class JobSearch(SQLModel):
    job_id: str


class JobLogs(SQLModel):
    id: int
    job_id: str
    cmd: str
    trigger: int
    exe_time: datetime
    stdout: Optional[str]
    status: int
    type: int


class JobLogSearch(SQLModel):
    job_id: Optional[str]
    cmd: Optional[str]
