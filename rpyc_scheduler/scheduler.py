from __future__ import print_function
from loguru import logger
from datetime import datetime, timedelta
import six
import warnings
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.base import MaxInstancesReachedError, BaseExecutor
from apscheduler.util import (timedelta_seconds, TIMEOUT_MAX)
from apscheduler.events import (JobSubmissionEvent, EVENT_JOB_SUBMITTED, EVENT_JOB_MAX_INSTANCES)

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

    def _process_jobs(self):
        """
        修改_process_jobs方法，把remove_job全部替换为pause_job，当任务执行完成后改成暂停状态
        """
        if self.state == STATE_PAUSED:
            self._logger.debug('Scheduler is paused -- not processing jobs')
            return None

        self._logger.debug('Looking for jobs to run')
        now = datetime.now(self.timezone)
        next_wakeup_time = None
        events = []

        with self._jobstores_lock:
            for jobstore_alias, jobstore in six.iteritems(self._jobstores):
                try:
                    due_jobs = jobstore.get_due_jobs(now)
                except Exception as e:
                    # Schedule a wakeup at least in jobstore_retry_interval seconds
                    self._logger.warning('Error getting due jobs from job store %r: %s',
                                         jobstore_alias, e)
                    retry_wakeup_time = now + timedelta(seconds=self.jobstore_retry_interval)
                    if not next_wakeup_time or next_wakeup_time > retry_wakeup_time:
                        next_wakeup_time = retry_wakeup_time

                    continue

                for job in due_jobs:
                    # Look up the job's executor
                    try:
                        executor = self._lookup_executor(job.executor)
                    except BaseException:
                        self._logger.error(
                            'Executor lookup ("%s") failed for job "%s" -- pause it from the '
                            'job store', job.executor, job)
                        self.pause_job(job.id, jobstore_alias)
                        continue

                    run_times = job._get_run_times(now)
                    run_times = run_times[-1:] if run_times and job.coalesce else run_times
                    if run_times:
                        try:
                            executor.submit_job(job, run_times)
                        except MaxInstancesReachedError:
                            self._logger.warning(
                                'Execution of job "%s" skipped: maximum number of running '
                                'instances reached (%d)', job, job.max_instances)
                            event = JobSubmissionEvent(EVENT_JOB_MAX_INSTANCES, job.id,
                                                       jobstore_alias, run_times)
                            events.append(event)
                        except BaseException:
                            self._logger.exception('Error submitting job "%s" to executor "%s"',
                                                   job, job.executor)
                        else:
                            event = JobSubmissionEvent(EVENT_JOB_SUBMITTED, job.id, jobstore_alias,
                                                       run_times)
                            events.append(event)

                        # 如果存在next_run_time，则更新
                        # 否则暂停此任务
                        job_next_run = job.trigger.get_next_fire_time(run_times[-1], now)
                        if job_next_run:
                            job._modify(next_run_time=job_next_run)
                            jobstore.update_job(job)
                        else:
                            self.pause_job(job.id, jobstore_alias)

                # Set a new next wakeup time if there isn't one yet or
                # the jobstore has an even earlier one
                jobstore_next_run_time = jobstore.get_next_run_time()
                if jobstore_next_run_time and (next_wakeup_time is None or
                                               jobstore_next_run_time < next_wakeup_time):
                    next_wakeup_time = jobstore_next_run_time.astimezone(self.timezone)

        # Dispatch collected events
        for event in events:
            self._dispatch_event(event)

        # Determine the delay until this method should be called again
        if self.state == STATE_PAUSED:
            wait_seconds = None
            self._logger.debug('Scheduler is paused; waiting until resume() is called')
        elif next_wakeup_time is None:
            wait_seconds = None
            self._logger.debug('No jobs; waiting until a job is added')
        else:
            wait_seconds = min(max(timedelta_seconds(next_wakeup_time - now), 0), TIMEOUT_MAX)
            self._logger.debug('Next wakeup is due at %s (in %f seconds)', next_wakeup_time,
                               wait_seconds)

        return wait_seconds
