from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, Integer, create_engine, Session
from sqlalchemy.dialects import mysql
from config import rpc_config


class TaskLog(SQLModel, table=True):
    id: Optional[int] = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    task_id: str = Field(max_length=20, sa_column_kwargs={'comment': '任务名'})
    status: int = Field(default=0, sa_column=Column(mysql.TINYINT, comment='执行命令返回状态'))
    exe_time: datetime = Field(default_factory=datetime.now, sa_column_kwargs={'comment': '任务执行时间'})
    cmd: str = Field(sa_column_kwargs={'comment': '执行命令'})
    type: int = Field(default=0, sa_column=Column(mysql.TINYINT, comment='类型：0单行命令，1：脚本文件'))
    stdout: str = Field(sa_column=Column(mysql.MEDIUMTEXT, comment='执行日志'))


engine = create_engine(rpc_config.apscheduler_job_store, pool_size=5, max_overflow=10, pool_timeout=30,
                       pool_pre_ping=True)
# SQLModel.metadata.create_all(engine)
session = Session(engine)
