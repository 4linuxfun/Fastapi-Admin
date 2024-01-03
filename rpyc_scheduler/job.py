from apscheduler.jobstores.base import BaseJobStore, JobLookupError, ConflictingIdError
from apscheduler.util import maybe_ref, datetime_to_utc_timestamp, utc_timestamp_to_datetime
from apscheduler.job import Job
try:
    import cPickle as pickle
except ImportError:  # pragma: nocover
    import pickle

try:
    from sqlalchemy import (
        create_engine, Table, Column, MetaData, Unicode, Float, LargeBinary, select, and_)
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.sql.expression import null
except ImportError:  # pragma: nocover
    raise ImportError('SQLAlchemyJobStore requires SQLAlchemy installed')


class MyJobStore(BaseJobStore):
    """
    参照apscheduler自带的SQLAlchemyJobStore，重写JobStore
    1. 添加额外的字段
    2. 重写部分方法，实现Job的保持
    """

    def __init__(self, url=None, engine=None, tablename='apscheduler_jobs', metadata=None,
                 pickle_protocol=pickle.HIGHEST_PROTOCOL, tableschema=None, engine_options=None):
        super().__init__(url=None, engine=None, tablename='apscheduler_jobs', metadata=None,
                         pickle_protocol=pickle.HIGHEST_PROTOCOL, tableschema=None, engine_options=None)
        self.jobs_t = Table(
            tablename, metadata,
            Column('id', Unicode(191), primary_key=True),
            Column('next_run_time', Float(25), index=True),
            Column('job_state', LargeBinary, nullable=False),
            schema=tableschema
        )

    def start(self, scheduler, alias):
        super().start(scheduler, alias)
