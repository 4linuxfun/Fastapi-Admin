from typing import Optional
from sqlmodel import Session
from fastapi import APIRouter, Depends
from ...db import get_session
from ... import crud
from ...schemas.internal.pagination import Pagination
from ...schemas.internal.sysapi import ApiSearch

router = APIRouter(prefix='/api', )


@router.post('/sysapis/search', summary='获取API列表')
async def get_sysapis(search: Pagination[ApiSearch],
                      session: Session = Depends(get_session)):
    print(search)
    total = crud.internal.api.search_total(session, search.search)
    print(total)
    sys_apis = crud.internal.api.search(session, search)
    return {
        'total': total,
        'data': sys_apis
    }


@router.get('/sysapis/{id}', summary='获取指定API', deprecated=True)
async def get_test(q: Optional[str] = None, direction: str = 'next', id: Optional[int] = 0,
                   limit: Optional[int] = None, offset_page: Optional[int] = None,
                   session: Session = Depends(get_session)):
    total = crud.internal.api.search_total(session, q)
    print(total)
    sysapis = crud.internal.api.search(session, q, direction, id, limit, offset_page)
    # users_list = [api for api in sysapis]
    # print(users_list)
    return {
        'total': total,
        'data': sysapis
    }
