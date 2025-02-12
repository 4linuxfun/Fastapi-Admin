from typing import Union
from loguru import logger
from sqlmodel import select, Session, delete
from ...models.internal.job import JobLogs
from ..base import CRUDBase


class CRUDJobLogs(CRUDBase[JobLogs]):
    def get_by_job_id(self, db: Session, job_id: str):
        return db.exec(select(self.model).where(self.model.job_id == job_id)).one()

    def delete_by_jobid(self, db: Session, job_id: str):
        db.exec(delete(self.model).where(self.model.job_id == job_id))
        db.commit()


job_logs = CRUDJobLogs(JobLogs)
