from typing import List
from loguru import logger
from apscheduler.util import maybe_ref
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy import (
    create_engine, Table, Column, MetaData, Unicode, Float, LargeBinary, select, and_, text, Integer)

try:
    import cPickle as pickle
except ImportError:  # pragma: nocover
    import pickle


class CustomJobStore(SQLAlchemyJobStore):

    def get_multi_jobs(self, uid=None):
        """
        通过job_id查询多个job
        """
        jobs = []
        selectable = select(self.jobs_t.c.id, self.jobs_t.c.job_state). \
            order_by(self.jobs_t.c.next_run_time)
        selectable = selectable.where(self.jobs_t.c.id == uid) if uid else selectable
        logger.debug(selectable)
        failed_job_ids = set()
        with self.engine.begin() as connection:
            for row in connection.execute(selectable):
                try:
                    jobs.append(self._reconstitute_job(row.job_state))
                except BaseException:
                    self._logger.exception('Unable to restore job "%s" -- removing it', row.id)
                    failed_job_ids.add(row.id)

            # Remove all the jobs we failed to restore
            if failed_job_ids:
                delete = self.jobs_t.delete().where(self.jobs_t.c.id.in_(failed_job_ids))
                connection.execute(delete)
        logger.debug(jobs)
        return jobs

    def get_user_jobs(self, uid, job_name, jobstore=None) -> list[Job]:
        """
        通过uid和job_name，获取用户的jobs列表
        :param uid:用户ID
        :param job_name：指定匹配job name
        :param jobstore: None
        """
        user_jobs: List[Job] = []
        jobs = self.get_multi_jobs(uid)
        logger.debug(jobs)
        for job in jobs:
            if job_name is None:
                user_jobs.append(job)
            elif (job.name.find(job_name)) >= 0:
                user_jobs.append(job)
        logger.debug(user_jobs)
        return user_jobs
