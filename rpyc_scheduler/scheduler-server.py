"""
远程调用apscheduler，参考：
https://github.com/agronholm/apscheduler/tree/3.x/examples/rpc
https://gist.github.com/gsw945/15cbb71eaca5be66787a2c187414e36f
"""

import rpyc
from tasks import subprocess_with_channel
from loguru import logger
from config import rpc_config
from rpyc.utils.server import ThreadedServer
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.events import (
    EVENT_JOB_EXECUTED,
    EVENT_JOB_ERROR,
    EVENT_JOB_ADDED,
    EVENT_JOB_SUBMITTED,
    EVENT_JOB_REMOVED
)


def print_text(*args, **kwargs):
    logger.debug(args)
    logger.debug(kwargs)


class SchedulerService(rpyc.Service):
    def exposed_add_job(self, func, *args, **kwargs):
        return scheduler.add_job(func, *args, **kwargs)

    def exposed_modify_job(self, job_id, jobstore=None, **changes):
        return scheduler.modify_job(job_id, jobstore, **changes)

    def exposed_pause_job(self, job_id, jobstore=None):
        return scheduler.pause_job(job_id, jobstore)

    def exposed_resume_job(self, job_id, jobstore=None):
        return scheduler.resume_job(job_id, jobstore)

    def exposed_remove_job(self, job_id, jobstore=None):
        return scheduler.remove_job(job_id, jobstore)

    def exposed_get_jobs(self, jobstore=None):
        return scheduler.get_jobs(jobstore)

    def exposed_get_job(self, job_id, jobstore=None):
        return scheduler.get_job(job_id, jobstore)


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
        'default': SQLAlchemyJobStore(url=rpc_config.apscheduler_job_store)
    }
    apscheduler_excutors = {
        'default': ThreadPoolExecutor(20),
        'processpool': ProcessPoolExecutor(20)
    }
    scheduler = BackgroundScheduler(jobstores=job_store,
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
