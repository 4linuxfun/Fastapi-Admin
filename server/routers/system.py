from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select, text
from sqlalchemy import func
from ..dependencies import get_session, check_token
from pydantic import BaseModel
from ..sql import crud
from ..sql.models import assets
from typing import List
from ..sql.schemas import ApiResponse
from ..common.utils import menu_convert

router = APIRouter(prefix='/api/assets', dependencies=[Depends(check_token), ])


class SearchForm(assets.System):
    limit: Optional[int]
    offset: Optional[int]


@router.post('/system/search_total')
async def search_total(system: SearchForm, session: Session = Depends(get_session)):
    total = session.execute(text("select count(id) from `system`;")).scalar()
    print(total)
    return ApiResponse(
        code=0,
        message="success",
        data=total
    )


@router.post('/system/search')
async def search_system(system: SearchForm, session: Session = Depends(get_session)):
    print(system)
    sql = select(assets.System)
    if system.type:
        sql = sql.where(assets.System.type.like('%' + system.type + '%'))
    if system.project:
        sql = sql.where(assets.System.project.like('%' + system.project + '%'))
    if system.host:
        sql = sql.where(assets.System.host.like('%' + system.host + '%'))
    sql = sql.offset(system.offset).limit(system.limit)
    print(str(sql))
    results = session.exec(sql).all()

    print(results)
    return ApiResponse(
        code=0,
        message="success",
        data=results
    )


@router.post('/system/import')
async def data_import(files: List[UploadFile] = File(...), session: Session = Depends(get_session)):
    # files参数是前后端统一规定的名字，如果需要修改，同意修改
    for file in files:
        print(file.filename)
        contents = await file.read()
        with open(f'{file.filename}', 'wb') as f:
            f.write(contents)
    return ApiResponse(
        code=0,
        message="success",
    )


@router.get('/system/down_temp')
async def download_tmpfile():
    print('down temp file')
    return FileResponse('机器学习数学.pdf',filename='机器学习数学.pdf')
