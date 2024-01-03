from typing import Optional, Any
from pydantic import BaseModel
from sqlmodel import SQLModel
from datetime import datetime


class JobSearch(SQLModel):
    job_name: Optional[str] = None


class JobLogs(SQLModel):
    id: int
    status: int
    start_time: datetime
    end_time: datetime
    log: Any
    job_id: str


class JobLogSearch(BaseModel):
    job_id: str
