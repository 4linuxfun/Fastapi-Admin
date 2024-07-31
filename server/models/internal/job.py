from enum import Enum
from typing import Union, List, Tuple, Dict, Any, Optional
from sqlmodel import SQLModel, Field, Column, Relationship, Integer, String, LargeBinary, JSON, Unicode
from sqlalchemy.dialects import mysql
from datetime import datetime
from pydantic import BaseModel


class CronJobArgs(BaseModel):
    cron: str
    start_date: Optional[str]
    end_date: Optional[str]


class TriggerEnum(str, Enum):
    date = 'date'
    cron = 'cron'


class TriggerArgs(BaseModel):
    run_date: Optional[str] = Field(default=None, description="date类型触发器设定执行时间，None为立即执行")
    cron: Optional[str] = Field(default=None, description="cron类型触发器参数")
    start_date: Optional[str] = Field(default=None, description="cron类型触发器开始时间")
    end_date: Optional[str] = Field(default=None, description="cron类型触发器结束时间")


class JobAdd(BaseModel):
    id: Optional[str] = Field(default=None, description="任务ID")
    name: str = Field(description="任务名称")
    trigger: TriggerEnum = Field(description="触发器类型")
    trigger_args: TriggerArgs = Field(description="触发器")
    targets: List[int] = Field(description="执行任务的主机")
    ansible_args: Dict[str, Any] = Field(default=None, description="ansible任务参数")


# class Job(SQLModel, table=True):
#     """
#     此表同步apschedule中的建表语句，如果没有，则apscheduler会自动创建对应表
#     """
#     __tablename__ = 'jobs'
#     id: str = Field(sa_column=Column('id', autoincrement=True, primary_key=True))
#     name: str = Field(sa_column=Column('name', String(50), nullable=False, unique=True))
#     create_time: float = Field(sa_column=Column('create_time', mysql.DOUBLE, index=True))
#     update_time: float = Field(sa_column=Column('update_time', mysql.DOUBLE, index=True))
#     job_id: str = Field(sa_column=Column('job_id', Unicode(255)))
#     job_logs: List["JobLog"] = Relationship(back_populates="job")
#
#
class JobLogs(SQLModel, table=True):
    __tablename__ = 'job_logs'
    id: Optional[int] = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    job_id: Optional[str] = Field(sa_column=Column('job_id', String(191), index=True))
    start_time: datetime = Field(default_factory=datetime.now, sa_column_kwargs={'comment': '任务开始时间'})
    end_time: datetime = Field(default=datetime.now, sa_column_kwargs={'comment': '任务结束时间'})
    log: str = Field(sa_column=Column(mysql.TEXT, comment='执行日志'))
    stats: str = Field(sa_column=Column(mysql.TEXT, comment='任务返回状态'))


class JobSearch(SQLModel):
    job_name: Optional[str] = None
    job_trigger: Optional[str] = None


class JobLogSearch(BaseModel):
    job_id: str
