from fastapi import APIRouter, Depends, Form
from ..dependencies import get_session, check_token, check_permission
from typing import Optional, List, Union
from ..common.security import hash_password
from pydantic import BaseModel
from sqlmodel import Session, select, or_
from sqlalchemy.exc import NoResultFound
from ..common.security import create_access_token
from ..common.utils import menu_convert
from ..sql import crud
from ..sql.models import Api, MenuApi
from ..sql.schemas import ApiResponse
from ..common import utils

router = APIRouter(prefix='/api')


@router.get('/sys-apis')
async def get_apis(q: Optional[str] = None, session: Session = Depends(get_session),
                   token: dict = Depends(check_token)):
    sql = select(Api)
    if q is not None:
        sql = sql.where(or_(Api.name.like('%' + q + '%'), Api.path.like('%' + q + '%')))
    apis = session.exec(sql).all()
    return ApiResponse(
        code=0,
        message="success",
        data=apis
    )


@router.post('/sys-apis')
async def add_apis(api: Api, session: Session = Depends(get_session)):
    session.add(api)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )


@router.put('/sys-apis')
async def update_apis(api: Api, session: Session = Depends(get_session)):
    sql = select(Api).where(Api.id == api.id)
    result = session.exec(sql).one()
    print(result)
    # menu_data = menu.dict(exclude_unset=True)
    # for key, value in menu_data.items():
    #     setattr(result, key, value)
    result = utils.update_model(result, api)
    session.add(result)
    session.commit()
    return ApiResponse(
        code=0,
        message="success"
    )


@router.delete('/sys-apis/{id}')
async def del_apis(id: int, session: Session = Depends(get_session)):
    sql = select(Api).where(Api.id == id)
    result = session.exec(sql).one()
    session.delete(result)
    session.commit()
    return ApiResponse(
        code=0,
        message="success"
    )
