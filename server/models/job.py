from typing import Union, List, Tuple, Dict, Any, Optional
from sqlmodel import SQLModel
from datetime import datetime
from pydantic import BaseModel


class DataJobArgs(BaseModel):
    run_date: Optional[datetime]


class CronJobArgs(BaseModel):
    cron: str
    start_date: Optional[str]
    end_date: Optional[str]


class CronJobAdd(BaseModel):
    job_id: str
    trigger: str
    date_args: Optional[DataJobArgs]
    cron_args: Optional[CronJobArgs]
    command: str
    type: str
