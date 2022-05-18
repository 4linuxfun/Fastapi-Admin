from typing import Optional
from sqlmodel import Session
from fastapi import APIRouter, Depends
from ..db import get_session
from .. import crud

router = APIRouter(prefix='/api', )


@router.get('/sysapis', summary='获取API列表')
async def get_sysapis(q: Optional[str] = None, direction: str = 'next', id: Optional[int] = 0,
                      limit: Optional[int] = None, offset_page: Optional[int] = None,
                      session: Session = Depends(get_session)):
    total = crud.api.search_total(session, q)
    print(total)
    sys_apis = crud.api.search(session, q, direction, id, limit, offset_page)
    return {
        'total': total,
        'data': sys_apis
    }


@router.get('/sysapis/{id}', summary='获取指定API', deprecated=True)
async def get_test(q: Optional[str] = None, direction: str = 'next', id: Optional[int] = 0,
                      limit: Optional[int] = None, offset_page: Optional[int] = None,
                      session: Session = Depends(get_session)):
    total = crud.api.search_total(session, q)
    print(total)
    sysapis = crud.api.search(session, q, direction, id, limit, offset_page)
    # users_list = [api for api in sysapis]
    # print(users_list)
    return {
        'total': total,
        'data': sysapis
    }
