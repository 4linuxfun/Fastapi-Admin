from typing import List, Union
from loguru import logger
from fastapi import APIRouter, Depends
from sqlmodel import Session
from server.common.response_code import ApiResponse, SearchResponse
from server.common.database import get_session
from server.models.internal.playbook import Playbook, PlaybookSearch
from server.models.internal import Pagination
from server import crud

router = APIRouter(prefix='/api')


@router.get('/playbook/{playbook_id}', summary='获取playbook详情', response_model=ApiResponse[Playbook])
async def get_playbook_by_id(playbook_id: int, session: Session = Depends(get_session)):
    playbook = crud.internal.playbook.get(session, playbook_id)
    return ApiResponse(data=playbook.model_dump())


@router.post('/playbook/search', summary="获取playbook列表", response_model=ApiResponse[SearchResponse[Playbook]])
async def get_all_user(search: Pagination[PlaybookSearch],
                       session: Session = Depends(get_session)):
    """
    :param search: Pagination实例，包含搜索的所有参数 偏移页面
    :param session:
    :return:
    """
    total = crud.internal.playbook.search_total(session, search.search, {'name': 'like'})
    logger.debug(total)
    playbooks: List[Playbook] = crud.internal.playbook.search(session, search, {'name': 'like'})
    playbook_list = [playbook.model_dump() for playbook
                     in playbooks]
    logger.debug(playbook_list)
    return ApiResponse(
        data={
            'total': total,
            'data': playbook_list
        }
    )


@router.get('/playbook', summary='获取playbooks列表', response_model=ApiResponse[List[Playbook]])
async def query_playbooks(query: Union[str, None] = None, session: Session = Depends(get_session)):
    playbooks: List[Playbook] = crud.internal.playbook.query_playbooks(session, query)
    playbook_list = [playbook.model_dump(exclude={'playbook'}) for playbook
                     in playbooks]
    return ApiResponse(data=playbook_list)


@router.post('/playbook', summary='创建playbook')
async def create_playbook(playbook: Playbook, session: Session = Depends(get_session)):
    logger.debug(playbook)
    crud.internal.playbook.insert(session, Playbook(**playbook.model_dump(exclude_unset=True)))
    return ApiResponse()


@router.put('/playbook', summary='更新playbook')
async def update_playbook(playbook: Playbook, session: Session = Depends(get_session)):
    crud.internal.playbook.update(session, crud.internal.playbook.get(session, playbook.id),
                                  Playbook(**playbook.model_dump(exclude_unset=True)))
    return ApiResponse()


@router.delete('/playbook/{book_id}', summary='删除playbook')
async def delete_playbook(book_id: int, session: Session = Depends(get_session)):
    crud.internal.playbook.delete(session, book_id)
    return ApiResponse()
