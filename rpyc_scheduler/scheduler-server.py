"""
远程调用apscheduler，参考：
https://github.com/agronholm/apscheduler/tree/3.x/examples/rpc
https://gist.github.com/gsw945/15cbb71eaca5be66787a2c187414e36f
"""

import redis
import rpyc
from loguru import logger
from typing import Dict
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


class Channel:
    def __init__(self, redis_config, task_id):
        logger.debug(f'__init__,redis:{redis_config},task id:{task_id}')
        self.conn = redis.Redis(**redis_config, decode_responses=True)
        self.task_id = task_id
        self.task_key = f"tasks:{self.task_id}"
        self._expire = 60

    @property
    def msg(self, ):
        return self.conn.xrange(self.task_key, '-', '+')

    @property
    def expire(self, ):
        return self._expire

    @expire.setter
    def expire(self, value):
        self._expire = value

    def send(self, msg: Dict[Any, Any]):
        self.conn.xadd(self.task_key, msg)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.expire(self.task_key, self._expire)
        self.close()

    def close(self, ):
        self.conn.close()


def subprocess_with_channel(task_id, command):
    with Channel(redis_config, task_id=task_id) as channel:
        channel.send({'msg': '开始执行任务：'})
        channel.send({'msg': f"执行命令：{command}"})
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   shell=True)
        while process.poll() is None:
            message = process.stdout.readline()
            channel.send({'msg': message})
        channel.send({'msg': '结束执行任务'})
        results = channel.msg
    return results


def print_text(text):
    logger.debug(text)


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
    # apscheduler相关服务启动
    jobstores = {
        'default': SQLAlchemyJobStore(url='mysql+pymysql://root:123456@192.168.137.129/devops')
    }
    excutors = {
        'default': ThreadPoolExecutor(20),
        'processpool': ProcessPoolExecutor(20)
    }
    scheduler = BackgroundScheduler(jobstores=jobstores, excutors=excutors)
    scheduler.add_listener(event_listener,
                           EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_ADDED | EVENT_JOB_REMOVED | EVENT_JOB_SUBMITTED)
    scheduler.start()

    # 启动rpyc服务
    server = ThreadedServer(SchedulerService, port=18861, protocol_config={'allow_public_attrs': True})
    try:
        server.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        scheduler.shutdown()
