from typing import Union
from loguru import logger
from sqlmodel import select, Session
from ...models.internal.job import JobLogs
from ..base import CRUDBase


class CRUDJobLogs(CRUDBase[JobLogs]):
    def get_by_job_id(self, db: Session, job_id: str):
        return db.exec(select(self.model).where(self.model.job_id == job_id)).one()


job_logs = CRUDJobLogs(JobLogs)
