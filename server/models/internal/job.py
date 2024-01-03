from enum import Enum
from typing import Union, List, Tuple, Dict, Any, Optional
from sqlmodel import SQLModel, Field, Column, Relationship, Integer, Unicode, LargeBinary, JSON
from sqlalchemy.dialects import mysql
from datetime import datetime
from pydantic import BaseModel
from .relationships import UserJob


class CronJobArgs(BaseModel):
    cron: str
    start_date: Optional[str]
    end_date: Optional[str]


class TriggerEnum(str, Enum):
    date = 'date'
    cron = 'cron'


class JobAdd(BaseModel):
    id: Optional[str] = None
    name: str
    targets: List[str]
    trigger: TriggerEnum
    trigger_args: Union[CronJobArgs, str] = None
    command: str
    type: str


class Job(SQLModel, table=True):
    """
    此表同步apschedule中的建表语句，如果没有，则apscheduler会自动创建对应表
    """
    __tablename__ = 'apscheduler_jobs'
    id: str = Field(sa_column=Column('id', Unicode(191), primary_key=True))
    next_run_time: float = Field(sa_column=Column('next_run_time', mysql.DOUBLE, index=True))
    job_state: bytes = Field(sa_column=Column('job_state', LargeBinary, nullable=False))
    logs: List["JobLog"] = Relationship(back_populates="job")
    user: "User" = Relationship(back_populates="jobs", link_model=UserJob)


class JobLog(SQLModel, table=True):
    __tablename__ = 'job_log'
    id: Optional[int] = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    status: int = Field(default=0, sa_column=Column(mysql.TINYINT, comment='执行命令返回状态'))
    start_time: datetime = Field(default_factory=datetime.now, sa_column_kwargs={'comment': '任务开始时间'})
    end_time: datetime = Field(default=datetime.now, sa_column_kwargs={'comment': '任务结束时间'})
    log: JSON = Field(sa_column=Column(JSON, comment='执行日志'))
    job_id: Optional[str] = Field(default=None, foreign_key="apscheduler_jobs.id")
    job: Optional[Job] = Relationship(back_populates="logs")

    class Config:
        arbitrary_types_allowed = True
