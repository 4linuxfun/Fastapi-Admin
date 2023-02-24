import rpyc
import copy
import re
from typing import Union, List, Any, Dict
from sqlmodel import SQLModel
from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger
from fastapi import APIRouter
from loguru import logger
from ..settings import settings
from ..models.job import CronJobAdd
from ..common.response_code import ApiResponse, SearchResponse
from ..schemas.internal.pagination import Pagination

router = APIRouter(prefix='/api/jobs')


class JobSearch(SQLModel):
    job_id: str


def cron_to_dict(cron):
    cron_list = re.split(r'\s+', cron)
    return {'minute': cron_list[0], 'hour': cron_list[1], 'day': cron_list[2], 'month': cron_list[3],
            'day_of_week': cron_list[4]}


@router.get('/pause/{job_id}', summary='暂停任务')
async def pause_job(job_id: str, ):
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        conn.root.pause_job(job_id)
    except Exception as e:
        logger.warning(e)
        return ApiResponse(
            code=500,
            message='暂停任务出错，请联系管理员！'
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
async def delete_job(job_id: str):
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        conn.root.remove_job(job_id)
    except Exception as e:
        logger.warning(e)
        return ApiResponse(
            code=500,
            message='删除任务出错，请联系管理员！'
        )
    return ApiResponse()


@router.put('/', summary='修改任务')
async def modify_job(job: CronJobAdd):
    cron_args = job.cron_args.dict()
    cron_args.update(cron_to_dict(job.cron_args.cron))
    del cron_args['cron']
    logger.debug(cron_args)
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        trigger = CronTrigger(**cron_args)
        conn.root.modify_job(job.job_id, trigger=trigger, kwargs={'task_id': job.job_id, 'command': job.command})
    except Exception as e:
        logger.warning(e)
        return ApiResponse(
            code=500,
            message=str(e)
        )


@router.post('/', summary='添加任务', response_model=ApiResponse[str])
async def add_job(job: CronJobAdd):
    logger.debug(job)
    if job.trigger == 'cron':
        trigger_args: Dict[str, Any] = job.cron_args.dict()
        trigger_args.update(cron_to_dict(job.cron_args.cron))
        del trigger_args['cron']
    else:
        trigger_args = job.date_args.dict()
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        job = conn.root.add_job('scheduler-server:subprocess_with_channel', trigger=job.trigger,
                                kwargs={'task_id': job.job_id, 'command': job.command}, id=job.job_id, **trigger_args)
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
async def show_jobs(search: Pagination[JobSearch]):
    job_id = search.search['job_id']
    try:
        conn = rpyc.connect(**settings.rpyc_config)
        if job_id is None:
            all_jobs: List[Job] = conn.root.get_jobs()
        else:
            search_job = conn.root.get_job(job_id)
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
    job_info_list: List[Dict[str, Any]] = []
    start = (search.page - 1) * search.page_size
    end = search.page * search.page_size - 1
    for job in all_jobs[start:end]:
        cron: Dict[str, str] = {}
        for field in job.trigger.fields:
            cron[field.name] = str(field)
        info = {
            'job_id': job.id,
            'next_run_time': job.next_run_time,
            'cron_args': {
                'cron': f"{cron['minute']} {cron['hour']} {cron['day']} {cron['month']} {cron['day_of_week']}",
                'start_date': None if job.trigger.start_date is None else job.trigger.start_date.strftime(
                    "%Y-%m-%d %H:%M:%S"),
                'end_date': None if job.trigger.end_date is None else job.trigger.end_date.strftime(
                    "%Y-%m-%d %H:%M:%S"),
            },
            'command': job.kwargs['command'],
            'status': 'running' if job.next_run_time is not None else 'stop'
        }
        job_info_list.append(info)
    return ApiResponse(
        data={
            'total': len(all_jobs),
            'data': job_info_list
        }
    )


@router.get('/logs')
async def job_logs():
    pass
