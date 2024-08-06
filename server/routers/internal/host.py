from typing import Optional, List
from uuid import uuid4

from loguru import logger
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from server.models.internal.host import Host, Group, GroupWithChild, CreateHost, HostWithIp
from server.common.utils import Tree
from server.models.internal import Pagination
from ...common.response_code import ApiResponse, SearchResponse
from ...common.database import get_session, get_rpyc
from ... import crud

router = APIRouter(prefix='/api')


@router.post('/host/group', summary='添加主机分组')
async def create_group(group: Group, session: Session = Depends(get_session)):
    try:
        crud.internal.group.insert(session, Group(**group.model_dump(exclude_unset=True)))
    except IntegrityError as e:
        logger.error(f"add Group Error:{str(e)}")
        return ApiResponse(
            code=500,
            message="组名已存在"
        )
    return ApiResponse()


@router.put('/host/group', summary='更新主机分组')
async def update_group(group: Group, session: Session = Depends(get_session)):
    crud.internal.group.update(session, crud.internal.group.get(session, group.id),
                               Group(**group.model_dump(exclude_unset=True)))
    return ApiResponse()


@router.get('/host/group', summary='获取所有组')
async def get_groups(session: Session = Depends(get_session)):
    groups: List[Group] = crud.internal.group.search_groups(session)
    nest_groups = Tree[GroupWithChild](groups, GroupWithChild).build()
    return ApiResponse(
        data=nest_groups
    )


@router.delete('/host/group/{group_id}', summary='删除组')
async def delete_group(group_id: int, session: Session = Depends(get_session)):
    group: Group = crud.internal.group.get(session, group_id)
    if len(group.hosts) > 0:
        return ApiResponse(
            code=500,
            message='此分组存在主机，请先迁移主机'
        )
    else:
        crud.internal.group.delete(session, group_id)
        return ApiResponse()


@router.post('/host', summary='新增主机')
async def create_host(host: CreateHost, session: Session = Depends(get_session)):
    groups = crud.internal.group.get_multi_by_ids(session, host.groups)
    crud.internal.host.insert(session, Host(**host.model_dump(exclude_unset=True, exclude={'groups'}),
                                            groups=groups))
    return ApiResponse()


@router.put('/host', summary='更新主机')
async def update_host(host: CreateHost, session: Session = Depends(get_session)):
    groups = crud.internal.group.get_multi_by_ids(session, host.groups)
    db_obj = crud.internal.host.get(session, host.id)
    db_obj = crud.internal.host.update(session, db_obj,
                                       Host(**host.model_dump(exclude_unset=True, exclude={'groups'})))
    db_obj.groups = groups
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    logger.debug(db_obj)
    return ApiResponse()


@router.delete('/host/{host_id}', summary='删除主机')
async def delete_host(host_id: int, session: Session = Depends(get_session)):
    crud.internal.host.delete(session, host_id)
    return ApiResponse()


@router.post('/host/search', summary="获取主机列表", response_model=ApiResponse[SearchResponse[Host]])
async def get_all_user(search: Pagination[HostWithIp],
                       session: Session = Depends(get_session)):
    """
    :param search: Pagination实例，包含搜索的所有参数 偏移页面
    :param session:
    :return:
    """
    total = crud.internal.host.search_total(session, search.search)
    logger.debug(total)
    hosts: List[Host] = crud.internal.host.search(session, search)
    hosts_list = [host.model_dump(exclude={'ansible_password', 'ansible_ssh_private_key'}) for host
                  in hosts]
    logger.debug(hosts_list)
    return ApiResponse(
        data={
            'total': total,
            'data': hosts_list
        }
    )


@router.get('/host/{id}', summary='获取主机信息')
async def get_host(id: int, session: Session = Depends(get_session)):
    host: Host = crud.internal.host.get(session, id)
    host_groups = [group.id for group in host.groups]
    return ApiResponse(
        data={**host.model_dump(exclude={'ansible_password', 'ansible_ssh_private_key'}), 'groups': host_groups}
    )


@router.get('/host/ping/{host_id}', summary="检查主机可用性")
async def host_ping_check(host_id: int, session: Session = Depends(get_session), rpyc=Depends(get_rpyc)):
    host: Host = crud.internal.host.get(session, host_id)
    inventory = {'all': {'hosts': {host.name: {**host.model_dump()}}}}
    logger.debug(inventory)
    job_id = uuid4().hex
    job = rpyc.root.add_job('scheduler-server:ansible_task', trigger='date', id=job_id,
                            kwargs={'job_id': job_id, 'targets': [host.id, ],
                                    'ansible_args': {'module': 'ping'}})
    return ApiResponse()
