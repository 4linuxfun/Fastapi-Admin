from fastapi import APIRouter, Depends, Form
from ..dependencies import get_session, check_token, check_permission
from typing import Optional, List, Union
from ..common.security import hash_password
from pydantic import BaseModel
from sqlmodel import Session, select,or_
from sqlalchemy.exc import NoResultFound
from ..common.security import create_access_token
from ..common.utils import menu_convert
from ..sql import crud
from ..sql.models import Api, MenuApi
from ..sql.schemas import ApiResponse
from ..common.utils import update_model

router = APIRouter(prefix='/api')


@router.get('/sys-apis')
async def get_apis(q: Optional[str] = None, session: Session = Depends(get_session),
                   token: dict = Depends(check_token)):
    sql = select(Api)
    if q is not None:
        sql = sql.where(or_(Api.name.like('%'+q+'%'),Api.path.like('%'+q+'%')))
    apis = session.exec(sql).all()
    return ApiResponse(
        code=0,
        message="success",
        data=apis
    )
