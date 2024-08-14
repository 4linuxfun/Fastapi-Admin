from typing import Union
from loguru import logger
from sqlmodel import select, Session
from ...models.internal.job import JobLogs
from ..base import CRUDBase


class CRUDJobLogs(CRUDBase[JobLogs]):
    pass


job_logs = CRUDJobLogs(JobLogs)
