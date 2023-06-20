import rpyc
import re
import anyio
from datetime import datetime
from uuid import uuid4
from typing import List, Any, Dict
from sqlmodel import Session, text
from apscheduler.job import Job
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from fastapi import APIRouter, Depends, WebSocket, Request
from loguru import logger
from server.settings import settings
from server.models.internal.job import JobAdd, JobLog
from server.common.database import get_session, get_redis
from server.common.response_code import ApiResponse, SearchResponse
from server.common.utils import get_task_logs
from server.schemas.internal.pagination import Pagination
from server.schemas.job import JobSearch, JobLogs, JobLogSearch
from server import crud
from server.common.dep import get_uid

router = APIRouter(prefix='/api/jobs')


def cron_to_dict(cron):
    cron_list = re.split(r'\s+', cron)
    return {'minute': cron_list[0], 'hour': cron_list[1], 'day': cron_list[2], 'month': cron_list[3],
            'day_of_week': cron_list[4]}


@router.get('/switch/{job_id}', summary='切换任务状态')
async def switch_job(job_id: str, ):
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        conn.root.switch_job(job_id)
    except ValueError as e:
        logger.warning(e)
        return ApiResponse(
            code=500,
            message=str(e)
        )
    return ApiResponse()


@router.get('/resume/{job_id}', summary='恢复任务')
async def resume_job(job_id: str):
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        conn.root.resume_job(job_id)
    except Exception as e:
        logger.warning(e)
        return ApiResponse(
            code=500,
            message='恢复任务出错，请联系管理员！'
        )
    return ApiResponse()


@router.delete('/{job_id}', summary='删除任务', response_model=ApiResponse[str])
async def delete_job(job_id: str, uid: int = Depends(get_uid), session: Session = Depends(get_session)):
    sql = text("select job_id from user_job where user_id=:uid")
    user_jobs = tuple([job[0] for job in session.execute(sql, {'uid': uid})])
    logger.debug(user_jobs)
    if job_id not in user_jobs:
        return ApiResponse(
            code=500,
            message='用户无权限操作此任务！'
        )
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        conn.root.pause_job(job_id)
        delete_user_job = text("delete from user_job where job_id=:job_id")
        session.execute(delete_user_job, {'job_id': job_id})
        delete_job_logs = text("delete from job_log where job_id=:job_id")
        session.execute(delete_job_logs, {'job_id': job_id})
        session.commit()
        conn.root.remove_job(job_id)
    except Exception as e:
        logger.warning(e)
        return ApiResponse(
            code=500,
            message='删除任务出错，请联系管理员！'
        )
    return ApiResponse()


@router.put('/', summary='修改任务', response_model=ApiResponse[str])
async def modify_job(job: JobAdd, session: Session = Depends(get_session)):
    logger.debug(job)
    if job.trigger == 'cron':
        trigger_args = job.trigger_args.dict()
        trigger_args.update(cron_to_dict(job.trigger_args.cron))
        del trigger_args['cron']
        trigger = CronTrigger(**trigger_args)
    elif job.trigger == 'date':
        trigger = DateTrigger(run_date=job.trigger_args, timezone=job.trigger.timezone)
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        conn.root.modify_job(job.id, kwargs={'job_id': job.id, 'command': job.command},
                             name=job.name, trigger=trigger)
    except Exception as e:
        logger.warning(e)
        return ApiResponse(
            code=500,
            message=str(e)
        )
    return ApiResponse()


@router.post('/', summary='添加任务', response_model=ApiResponse[str])
async def add_job(job: JobAdd, uid: int = Depends(get_uid), session: Session = Depends(get_session)):
    logger.debug(job)
    # 手动生成job_id，需要传递到内部
    job_id = uuid4().hex
    # 只支持cron的date任务，interval间隔任务完全可以用cron替代，没必要单独实现功能
    if job.trigger == 'cron':
        trigger_args: Dict[str, Any] = job.trigger_args.dict()
        trigger_args.update(cron_to_dict(job.trigger_args.cron))
        del trigger_args['cron']
    elif job.trigger == 'date':
        trigger_args = {'run_date': job.trigger_args}
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        job = conn.root.add_job('scheduler-server:run_command_with_channel', trigger=job.trigger.value,
                                kwargs={'job_id': job_id,
                                        'command': job.command}, id=job_id, name=job.name, **trigger_args)
        sql = text("INSERT INTO user_job values (:uid,:job_id)")
        session.execute(sql, {'uid': uid, "job_id": job_id})
        session.commit()
    except Exception as e:
        logger.warning(e)
        return ApiResponse(
            code=500,
            message=str(e)
        )
    return ApiResponse(
        data=job.id
    )


@router.post('/search', summary='获取所有任务', response_model=ApiResponse[SearchResponse[Any]])
async def show_jobs(search: Pagination[JobSearch], uid: int = Depends(get_uid),
                    session: Session = Depends(get_session)):
    job_name = search.search['job_name']
    sql = text("select job_id from user_job where user_id=:uid ")
    results = session.execute(sql, {'uid': uid})
    user_job_ids: List[str] = []
    for job_id in results.fetchall():
        user_job_ids.append(job_id[0])
    logger.debug(f'uid:{uid},jobs:{user_job_ids}')
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        if job_name is None:
            all_jobs: List[Job] = conn.root.get_jobs()
        else:
            search_job = conn.root.get_job(job_name)
            if search_job is None:
                all_jobs: List[Job] = []
            else:
                all_jobs: List[Job] = [search_job]
    except Exception as e:
        logger.warning(e)
        return ApiResponse(
            code=500,
            message=str(e)
        )
    if len(all_jobs) == 0:
        return ApiResponse(
            data={
                'total': len(all_jobs),
                'data': []
            }
        )

    user_jobs = [job for job in all_jobs if job.id in user_job_ids]
    logger.debug(user_jobs)

    job_info_list: List[Dict[str, Any]] = []
    start = (search.page - 1) * search.page_size
    end = search.page * search.page_size - 1
    for job in user_jobs[start:end]:
        logger.debug(job.trigger)
        trigger_args: Dict[str, str] = {}
        info = {}
        if isinstance(job.trigger, CronTrigger):
            logger.debug('cron')
            for field in job.trigger.fields:
                trigger_args[field.name] = str(field)
            info.update({
                'id': job.id,
                'name': job.name,
                'trigger': 'cron',
                'trigger_args': {
                    'cron': f"{trigger_args['minute']} {trigger_args['hour']} {trigger_args['day']} {trigger_args['month']} {trigger_args['day_of_week']}",
                    'start_date': None if job.trigger.start_date is None else job.trigger.start_date.strftime(
                        "%Y-%m-%d %H:%M:%S"),
                    'end_date': None if job.trigger.end_date is None else job.trigger.end_date.strftime(
                        "%Y-%m-%d %H:%M:%S"),
                },
                'command': job.kwargs['command'],
                'status': 'running' if job.next_run_time is not None else 'stop'
            })
        elif isinstance(job.trigger, DateTrigger):
            info.update({
                'id': job.id,
                'name': job.name,
                'trigger': 'date',
                'trigger_args': job.trigger.run_date.strftime(
                    "%Y-%m-%d %H:%M:%S"),
                'command': job.kwargs['command'],
                'status': 'running' if job.next_run_time is not None else 'stop'
            })
        logger.debug(info)
        job_info_list.append(info)
    logger.debug(job_info_list)
    return ApiResponse(
        data={
            'total': len(user_jobs),
            'data': job_info_list
        }
    )


@router.post('/logs', summary='任务日志查询', response_model=ApiResponse[SearchResponse[JobLogs]])
async def job_logs(page_search: Pagination[JobLogSearch], session: Session = Depends(get_session)):
    filter_type = JobLogSearch(job_id='like', cmd='like')
    total = crud.internal.job_log.search_total(session, page_search.search, filter_type.dict())
    jobs = crud.internal.job_log.search(session, page_search, filter_type.dict())
    logger.debug(jobs)
    return ApiResponse(
        data={
            'total': total,
            'data': jobs
        }
    )


@router.websocket('/logs/ws/')
async def websocket_endpoint(id: int, job_id: str, trigger: str, websocket: WebSocket,
                             session: Session = Depends(get_session),
                             redis=Depends(get_redis)):
    await websocket.accept()
    async with anyio.create_task_group() as tg:
        tg.start_soon(get_task_logs, websocket, redis, session, task_id, trigger)
    logger.debug('close websocket')
    await websocket.close()
