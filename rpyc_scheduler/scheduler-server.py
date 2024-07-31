"""
远程调用apscheduler，参考：
https://github.com/agronholm/apscheduler/tree/3.x/examples/rpc
https://gist.github.com/gsw945/15cbb71eaca5be66787a2c187414e36f
"""

import rpyc
from typing import List

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from sqlmodel import text
from tasks import *
from datetime import datetime
from loguru import logger
from config import rpc_config
from rpyc.utils.server import ThreadedServer
from apscheduler.job import Job
# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.events import (
    EVENT_JOB_EXECUTED,
    EVENT_JOB_ERROR,
    EVENT_JOB_ADDED,
    EVENT_JOB_SUBMITTED,
    EVENT_JOB_REMOVED
)
from jobstore import CustomJobStore
from scheduler import CustomBackgroundScheduler
from models import engine


def print_text(*args, **kwargs):
    logger.debug(args)
    logger.debug(kwargs)


class SchedulerService(rpyc.Service):
    def exposed_add_job(self, func, **kwargs):
        trigger = kwargs.pop('trigger', None)
        trigger_args = kwargs.pop('trigger_args', None)
        if trigger == 'cron':
            cron = trigger_args['cron']
            values = cron.split()
            trigger = CronTrigger(minute=values[0], hour=values[1], day=values[2], month=values[3],
                                  day_of_week=values[4], start_date=trigger_args['start_date'],
                                  end_date=trigger_args['end_date'])
            return scheduler.add_job(func, CronTrigger.from_crontab(trigger), **kwargs)
        elif trigger == 'date':
            return scheduler.add_job(func, DateTrigger(
                run_date=trigger_args['run_date'] if trigger_args is not None else None), **kwargs)

    def exposed_modify_job(self, job_id, jobstore=None, **changes):
        logger.debug(changes)
        trigger = changes.pop('trigger', 'date')
        trigger_args = changes.pop('trigger_args', None)
        if trigger == 'cron':
            cron = trigger_args['cron']
            values = cron.split()
            changes['trigger'] = CronTrigger(minute=values[0], hour=values[1], day=values[2], month=values[3],
                                             day_of_week=values[4], start_date=trigger_args['start_date'],
                                             end_date=trigger_args['end_date'])
        else:
            run_date = trigger_args['run_date']
            changes['trigger'] = DateTrigger(run_date=run_date, timezone=None)
        logger.debug(changes)
        return scheduler.modify_job(job_id, jobstore, **changes)

    def exposed_pause_job(self, job_id):
        return scheduler.pause_job(job_id)

    def exposed_resume_job(self, job_id):
        return scheduler.resume_job(job_id)

    def exposed_remove_job(self, job_id):
        return scheduler.remove_job(job_id)

    def exposed_get_jobs(self, jobstore=None):
        return scheduler.get_jobs(jobstore)

    def exposed_get_job(self, job_id, jobstore=None):
        return scheduler.get_job(job_id, jobstore)

    def exposed_get_multi_jobs(self, job_ids, jobstore=None) -> list[Job]:
        """
        通过job_ids，获取jobs列表
        :param job_ids:
        :param jobstore: None
        """
        logger.debug(f'get_multi_jobs:{job_ids}')
        jobs = []
        for job_id in job_ids:
            job = self.exposed_get_job(job_id, jobstore)
            jobs.append(job)
        return jobs

    def exposed_get_user_jobs(self, uid=None, job_name=None, jobstore=None) -> list[Job]:
        """
        通过uid和job_name，获取用户的jobs列表
        :param uid:用户ID
        :param job_name：指定匹配job name
        :param jobstore: None
        """
        logger.debug('get user jobs')
        return scheduler.get_user_jobs(uid, job_name, jobstore)


def event_listener(event):
    if event.code == EVENT_JOB_ADDED:
        logger.debug('event add')
    elif event.code == EVENT_JOB_EXECUTED:
        logger.debug('event executed')
    elif event.code == EVENT_JOB_REMOVED:
        logger.debug('event removed')
    elif event.code == EVENT_JOB_ERROR:
        logger.debug('event error')


if __name__ == '__main__':
    job_store = {
        'default': CustomJobStore(url=str(rpc_config.apscheduler_job_store))
    }
    apscheduler_excutors = {
        'default': ThreadPoolExecutor(20),
        'processpool': ProcessPoolExecutor(20)
    }
    scheduler = CustomBackgroundScheduler(jobstores=job_store,
                                          excutors=apscheduler_excutors)
    scheduler.add_listener(event_listener,
                           EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_ADDED | EVENT_JOB_REMOVED | EVENT_JOB_SUBMITTED)
    scheduler.start()

    # 启动rpyc服务
    server = ThreadedServer(SchedulerService, port=rpc_config.rpc_port,
                            protocol_config={'allow_public_attrs': True, 'allow_pickle': True})
    try:
        server.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        scheduler.shutdown()
