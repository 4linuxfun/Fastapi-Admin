from __future__ import print_function
from loguru import logger
from datetime import datetime, timedelta
import six
import warnings
from apscheduler.schedulers.background import BackgroundScheduler

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

STATE_STOPPED = 0
#: constant indicating a scheduler's running state (started and processing jobs)
STATE_RUNNING = 1
#: constant indicating a scheduler's paused state (started but not processing jobs)
STATE_PAUSED = 2


class CustomBackgroundScheduler(BackgroundScheduler):

    def get_user_jobs(self, uid, job_name, jobstore=None, pending=None):
        """
        分页搜索jobs

        :param str|unicode jobstore: alias of the job store
        :param bool pending: **DEPRECATED**
        :rtype: list[Job]

        """
        if pending is not None:
            warnings.warn('The "pending" option is deprecated -- get_jobs() always returns '
                          'scheduled jobs if the scheduler has been started and pending jobs '
                          'otherwise', DeprecationWarning)

        with self._jobstores_lock:
            jobs = []
            if self.state == STATE_STOPPED:
                for job, alias, replace_existing in self._pending_jobs:
                    if jobstore is None or alias == jobstore:
                        jobs.append(job)
            else:
                for alias, store in six.iteritems(self._jobstores):
                    if jobstore is None or alias == jobstore:
                        jobs.extend(store.get_user_jobs(uid, job_name, jobstore))
            logger.debug(jobs)
            return jobs

    def get_jobs(self, jobstore=None, pending=None):
        """
        分页搜索jobs

        :param str|unicode jobstore: alias of the job store
        :param bool pending: **DEPRECATED**
        :rtype: list[Job]

        """
        if pending is not None:
            warnings.warn('The "pending" option is deprecated -- get_jobs() always returns '
                          'scheduled jobs if the scheduler has been started and pending jobs '
                          'otherwise', DeprecationWarning)

        with self._jobstores_lock:
            jobs = []
            if self.state == STATE_STOPPED:
                for job, alias, replace_existing in self._pending_jobs:
                    if jobstore is None or alias == jobstore:
                        jobs.append(job)
            else:
                for alias, store in six.iteritems(self._jobstores):
                    if jobstore is None or alias == jobstore:
                        jobs.extend(store.get_all_jobs())
            return jobs
