from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile
from starlette.background import BackgroundTask
from fastapi.responses import FileResponse
from sqlmodel import Session, select, text
from ..dependencies import get_session, check_token
from ..sql.models import assets
from typing import List
from ..sql.schemas import ApiResponse
import pandas as pd
from ..sql.database import engine
from tempfile import NamedTemporaryFile
from ..common import utils

router = APIRouter(prefix='/api/assets', dependencies=[Depends(check_token), ])


class SearchForm(assets.System):
    limit: Optional[int]
    offset: Optional[int]


@router.post('/system/search_total')
async def search_total(system: SearchForm, session: Session = Depends(get_session)):
    sql = "select count(id) from `system` where 1=1 "
    if system.type:
        sql += f" and type like '%{system.type}%' "
    if system.ip:
        sql += f" and ip like '%{system.ip}%' "
    if system.project:
        sql += f""" and project like '%{system.project}%'"""
    if system.host:
        sql += f" and host like '%{system.host}%' "
    sql += ';'
    print(sql)
    total = session.execute(text(sql)).scalar()
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
    if system.ip:
        sql = sql.where(assets.System.ip.like('%' + system.ip + '%'))
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
        contents = file.read()
        excel_data = pd.read_excel(contents, )
        excel_data.rename(
            columns={"主机名": "host", "IP地址": "ip", "操作系统": "system", "CPU数量": "cpu", "空间": "storage", "内存": "memory",
                     "管理员": "admin", "环境": "env", "类型": "type", "项目": "project", "三线开发": "developer"}, inplace=True)
        excel_data.to_sql('system', engine, if_exists='append', index=False, method='multi')
        print(excel_data)
    return ApiResponse(
        code=0,
        message="success",
    )


@router.get('/system/down_temp')
async def download_tmpfile():
    print('down temp file')
    return FileResponse('server/static/template/system.xlsx', filename='system.xlsx')


@router.post("/system/output")
def output_data(system: SearchForm, session:Session=Depends(get_session) ):
    sql = select(assets.System)
    if system.type:
        sql = sql.where(assets.System.type.like('%' + system.type + '%'))
    if system.ip:
        sql = sql.where(assets.System.ip.like('%' + system.ip + '%'))
    if system.project:
        sql = sql.where(assets.System.project.like('%' + system.project + '%'))
    if system.host:
        sql = sql.where(assets.System.host.like('%' + system.host + '%'))
    select_data = pd.read_sql_query(sql, session.bind)
    select_data.rename(
        columns={"host": "主机名", "ip": "IP地址", "system": "操作系统", "cpu": "CPU数量", "storage": "空间", "memory": "内存",
                 "admin": "管理员", "env": "环境", "type": "类型", "project": "项目", "developer": "三线开发"}, inplace=True)
    select_data.drop(columns=['id'], inplace=True)
    print(select_data)
    with NamedTemporaryFile('w+b', suffix='.xlsx', delete=False) as f:
        select_data.to_excel(f)
        return FileResponse(f.name, filename='导出.xlsx', background=BackgroundTask(utils.remove_tmp_file, f.name))
