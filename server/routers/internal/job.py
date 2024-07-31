import rpyc
import re
import anyio
from datetime import datetime
from uuid import uuid4
from typing import List, Any, Dict, TYPE_CHECKING
from sqlmodel import Session, text
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from fastapi import APIRouter, Depends, WebSocket, Request
from loguru import logger
from server.settings import settings
from server.models.internal.job import JobAdd
from server.common.database import get_session, get_redis, get_rpyc
from server.common.response_code import ApiResponse, SearchResponse
from server.common.utils import get_task_logs
from server.models.internal import Pagination
from server.models.internal.job import JobSearch, JobLogs, JobLogSearch
from server import crud
from server.common.dep import get_uid

# if TYPE_CHECKING:
#     from apscheduler.job import Job

router = APIRouter(prefix='/api/jobs')


@router.get('/switch/{job_id}', summary='任务状态切换')
async def switch_job(job_id: str, status: int):
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        if status == 1:
            conn.root.resume_job(job_id)
        else:
            conn.root.pause_job(job_id)
    except ValueError as e:
        logger.warning(e)
        return ApiResponse(
            code=500,
            message=str(e)
        )
    return ApiResponse()


@router.delete('/{job_id}', summary='删除任务', response_model=ApiResponse[str])
async def delete_job(job_id: str, uid: int = Depends(get_uid), session: Session = Depends(get_session)):
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        conn.root.pause_job(job_id)
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
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        conn.root.modify_job(job.id,
                             kwargs={'job_id': job.id, 'targets': job.targets, 'ansible_args': job.ansible_args},
                             name=job.name, trigger=job.trigger, trigger_args=job.trigger_args.model_dump())
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
    # 手动生成job_id，传入执行函数，方便后期日志写入redis
    job_id = uuid4().hex
    logger.debug(f'user defined job ID:{job_id}')
    # 只支持cron和date任务，interval间隔任务完全可以用cron替代，没必要单独实现功能
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        job = conn.root.add_job('scheduler-server:ansible_task', trigger=job.trigger, id=job_id,
                                kwargs={'job_id': job_id, 'targets': job.targets,
                                        'ansible_args': job.ansible_args}, name=job.name,
                                trigger_args=job.trigger_args.model_dump())
        logger.debug(job.id)
    except Exception as e:
        logger.warning(e)
        return ApiResponse(
            code=500,
            message=str(e)
        )
    return ApiResponse(
        message=f'新建任务成功：{job.name}'
    )


@router.post('/search', summary='获取所有任务', response_model=ApiResponse[SearchResponse[Any]])
async def show_jobs(search: Pagination[JobSearch], uid: int = Depends(get_uid), conn: Any = Depends(get_rpyc)):
    # job_name = search.search.job_name
    try:
        user_jobs = conn.root.get_user_jobs(uid=None)
        logger.debug(user_jobs)
    except Exception as e:
        logger.warning(e)
        return ApiResponse(
            code=500,
            message=str(e)
        )
    if len(user_jobs) == 0:
        return ApiResponse(
            data={
                'total': 0,
                'data': []
            }
        )

    logger.debug(user_jobs)

    job_info_list: List[Dict[str, Any]] = []
    start = (search.page - 1) * search.page_size
    end = search.page * search.page_size - 1
    for job in user_jobs[start:end]:
        logger.debug(job.trigger)
        logger.debug(job.kwargs)
        trigger_args: Dict[str, str] = {}
        info = {}
        if isinstance(job.trigger, CronTrigger):
            logger.debug('cron')
            for field in job.trigger.fields:
                trigger_args[field.name] = str(field)
            # job.kwargs['targets']默认为rpyc类型的list，需要转成python的list类型，否则pydantic类型检查会去找rpyc list，报错
            info.update({
                'id': str(job.id),
                'name': str(job.name),
                'targets': list(job.kwargs['targets']),
                'trigger': 'cron',
                'trigger_args': {
                    'cron': f"{trigger_args['minute']} {trigger_args['hour']} {trigger_args['day']} {trigger_args['month']} {trigger_args['day_of_week']}",
                    'start_date': None if job.trigger.start_date is None else job.trigger.start_date.strftime(
                        "%Y-%m-%d %H:%M:%S"),
                    'end_date': None if job.trigger.end_date is None else job.trigger.end_date.strftime(
                        "%Y-%m-%d %H:%M:%S"),
                    'run_date': None,
                },
                'ansible_args': dict(job.kwargs['ansible_args']),
                'status': '1' if job.next_run_time is not None else '0'
            })
        elif isinstance(job.trigger, DateTrigger):
            info.update({
                'id': str(job.id),
                'name': str(job.name),
                'targets': list(job.kwargs['targets']),
                'trigger': 'date',
                'trigger_args': {
                    'run_date': str(job.trigger.run_date.strftime(
                        "%Y-%m-%d %H:%M:%S")),
                    'cron': None,
                    'start_date': None,
                    'end_date': None,
                },
                'ansible_args': dict(job.kwargs['ansible_args']),
                'status': '1' if job.next_run_time is not None else '0'
            })
        logger.debug(info)
        job_info_list.append(info)
    logger.debug(job_info_list)
    return ApiResponse(
        data={
            'total': 10,
            'data': job_info_list
        }
    )


@router.post('/logs', summary='任务日志查询', response_model=ApiResponse[SearchResponse[JobLogs]])
async def job_logs(page_search: Pagination[JobLogSearch], session: Session = Depends(get_session)):
    logger.debug(page_search)
    total = crud.internal.job_logs.search_total(session, page_search.search, filter_type={'job_id': 'eq'})
    jobs = crud.internal.job_logs.search(session, page_search, filter_type={'job_id': 'eq'})
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
