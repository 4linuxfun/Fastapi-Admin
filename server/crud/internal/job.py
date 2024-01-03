from typing import Union
from loguru import logger
from sqlmodel import select, Session
from ...models.internal.job import JobLog
from ..base import CRUDBase
from .roles import role


class CRUDJobLog(CRUDBase[JobLog]):
    pass


job_log = CRUDJobLog(JobLog)
