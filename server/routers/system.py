from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile
from starlette.background import BackgroundTask
from fastapi.responses import FileResponse
from sqlmodel import Session, select, text
from sqlalchemy import func
from ..dependencies import get_session, check_token
from ..sql.models import assets
from typing import List
from ..sql.schemas import ApiResponse
import pandas as pd
from ..sql.database import engine
from tempfile import NamedTemporaryFile
from ..common import utils
import json

router = APIRouter(prefix='/api/assets', dependencies=[Depends(check_token), ])


class SearchForm(assets.Assets):
    limit: Optional[int]
    offset: Optional[int]


@router.post('/system/search_total')
async def search_total(system: SearchForm, session: Session = Depends(get_session)):
    sql = select(func.count(assets.Assets.id))
    print(sql)
    if system.category:
        sql = sql.where(assets.Assets.category.like('%' + system.category + '%'))
    if system.manager:
        sql = sql.where(assets.Assets.manager.like('%' + system.manager + '%'))
    if system.area:
        sql = sql.where(assets.Assets.area.like('%' + system.area + '%'))
    if system.user:
        sql = sql.where(assets.Assets.user.like('%' + system.user + '%'))
    for key, value in system.info.items():
        if value:
            sql = sql.where(assets.Assets.info[key].like('%' + value + '%'))
        print(f'{key}:{value}')
    print(sql)
    total = session.execute(sql).scalar()
    # print(system)
    # sql = "select count(id) from `system` where 1=1 "
    # if system.type:
    #     sql += f" and type like '%{system.type}%' "
    # if system.ip:
    #     sql += f" and ip like '%{system.ip}%' "
    # if system.project:
    #     sql += f""" and project like '%{system.project}%'"""
    # if system.host:
    #     sql += f" and host like '%{system.host}%' "
    # sql += f" and info"
    # sql += ';'
    # print(sql)
    # total = session.execute(text(sql)).scalar()
    print(total)
    return ApiResponse(
        code=0,
        message="success",
        data=total
    )


@router.post('/system/search')
async def search_system(system: SearchForm, session: Session = Depends(get_session)):
    print(system)
    sql = select(assets.Assets)
    if system.category:
        sql = sql.where(assets.Assets.category.like('%' + system.category + '%'))
    if system.manager:
        sql = sql.where(assets.Assets.manager.like('%' + system.manager + '%'))
    if system.area:
        sql = sql.where(assets.Assets.area.like('%' + system.area + '%'))
    if system.user:
        sql = sql.where(assets.Assets.user.like('%' + system.user + '%'))
    for key, value in system.info.items():
        if value:
            sql = sql.where(assets.Assets.info[key].like('%' + value + '%'))
        print(f'{key}:{value}')
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
    """
    每个导入的文件，都存在静态字段、动态字段，需要对动态字段转换成json格式的字符串，然后才能进行插入
    :param files: files参数是前后端统一规定的名字，如果需要修改，同意修改
    :param session:
    :return:
    """
    for file in files:
        print(file.filename)
        contents = await file.read()
        excel_data = pd.read_excel(contents, engine='openpyxl')
        col_list = excel_data.columns.values.tolist()
        print(col_list)
        static_dict = {"主机名": "host", "IP地址": "ip", "操作系统": "system", "CPU数量": "cpu", "空间": "storage", "内存": "memory",
                       "管理员": "admin", "环境": "env", "类型": "type", "项目": "project", "三线开发": "developer"}
        static_list = static_dict.keys()
        dynamic_list = list(set(col_list) - set(static_list))
        print(dynamic_list)
        dynamic_data = excel_data[dynamic_list]
        print(dynamic_data)
        # 静态字段统一修改中文为英文（数据库表字段为英文）
        excel_data.rename(
            columns={"主机名": "host", "IP地址": "ip", "操作系统": "system", "CPU数量": "cpu", "空间": "storage", "内存": "memory",
                     "管理员": "admin", "环境": "env", "类型": "type", "项目": "project", "三线开发": "developer"}, inplace=True)

        print(excel_data)
        excel_data['info'] = excel_data.apply(to_json, axis=1, args=(dynamic_list,))

        excel_data.drop(columns=dynamic_list, inplace=True)
        print(excel_data)
        excel_data.to_sql('system', engine, if_exists='append', index=False, method='multi')
    return ApiResponse(
        code=0,
        message="success",
    )


@router.get('/system/down_temp')
async def download_tmpfile():
    print('down temp file')
    return FileResponse('server/static/template/system.xlsx', filename='system.xlsx')


@router.get('/category-list')
async def get_category_list(session: Session = Depends(get_session)):
    categories = session.exec(select(assets.Category)).all()
    category_list = [cate.dict(exclude={'alias': True, 'desc': True}) for cate in categories]
    print(category_list)
    return ApiResponse(
        code=0,
        message="success",
        data=category_list
    )


@router.get('/category_field/{id}')
async def get_category_field(id: int, session: Session = Depends(get_session)):
    fields = session.exec(select(assets.CategoryField).where(assets.CategoryField.category_id == id)).all()
    print(fields)
    return ApiResponse(
        code=0,
        message="success",
        data=fields
    )


@router.post("/system/output")
def output_data(system: SearchForm, session: Session = Depends(get_session)):
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
        return FileResponse(f.name, filename='output.xlsx', background=BackgroundTask(utils.remove_tmp_file, f.name))


def to_json(x, dynamic_list):
    print(x)
    info = {}
    for value in dynamic_list:
        info[value] = x[value]
    return json.dumps(info)
