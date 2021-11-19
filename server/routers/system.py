from typing import Optional
import sqlalchemy.exc
from fastapi import APIRouter, Depends, File, UploadFile
from starlette.background import BackgroundTask
from fastapi.responses import FileResponse
from sqlmodel import Session, select, text
from sqlalchemy import func
from ..dependencies import get_session, check_token
from ..sql.models import assets
from typing import List, Union, Dict, Any
from pydantic import BaseModel
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


class UpdateCategory(BaseModel):
    category: assets.Category
    fields: List[assets.CategoryField]


class UpdateAssets(BaseModel):
    # 批量更新资产信息提交内容
    assets: List[int]
    update: List[Dict[str, Any]]


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
    if not system.category:
        return ApiResponse(
            code=1,
            message="error",
            data='请选择资产类型'
        )
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
async def get_category_list(search: Optional[str] = None, session: Session = Depends(get_session)):
    sql = select(assets.Category)
    if search is not None:
        sql = sql.where(assets.Category.name.like('%' + search + '%'))
    categories: List[assets.Category] = session.exec(sql).all()
    # category_list = [cate.dict(exclude={'alias': True, 'desc': True}) for cate in categories]
    # print(category_list)
    return ApiResponse(
        code=0,
        message="success",
        data=categories
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


@router.get('/category_detail/{id}')
async def get_category_detail(id: int, session: Session = Depends(get_session)):
    category: assets.Category = session.exec(select(assets.Category).where(assets.Category.id == id)).one()
    print(category)
    return ApiResponse(
        code=0,
        message="success",
        data={
            'category': category,
            'fields': category.fields
        }
    )


@router.get('/asset_field/{id}', description='获取对应资产的定义字段')
async def get_asset_fields(id: int, session: Session = Depends(get_session)):
    fields = session.exec(select(assets.CategoryField).where(assets.CategoryField.category_id == id)).all()
    info_fields = []
    for field in fields:
        info_fields.append({'label': field.desc, 'value': field.name})
    return ApiResponse(
        code=0,
        message="success",
        data=[
            {
                'label': '通用字段',
                'options': [
                    {
                        'label': '资产类别',
                        'value': 'category'
                    },
                    {
                        'label': '使用人',
                        'value': 'user'
                    },
                    {
                        'label': '管理员',
                        'value': 'manager'
                    },
                    {
                        'label': '区域',
                        'value': 'area'
                    }
                ]
            },
            {
                'label': '专用字段',
                'options': info_fields
            }
        ]
    )


@router.post('/update_assets', description="批量更新资产信息")
async def update_assets(update: UpdateAssets, session: Session = Depends(get_session)):
    print(update)
    assets_result = session.exec(select(assets.Assets).where(assets.Assets.id.in_(update.assets)))
    print(assets_result)
    for asset in assets_result:
        print(asset)
        for new in update.update:
            if new['name'] == 'category':
                asset.category = new['value']
            elif new['name'] == 'manager':
                asset.manager = new['value']
            elif new['name'] == 'user':
                asset.user = new['value']
            elif new['name'] == 'area':
                asset.area = new['value']
            else:
                asset.info[new['name']] = new['value']
        session.add(asset)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )


@router.post('/update_category_detail')
async def update_category_detail(update_category: assets.Assets, session: Session = Depends(get_session)):
    category = session.exec(select(assets.Assets).where(assets.Assets.id == update_category.id)).one()
    category = utils.update_model(category, update_category)
    session.add(category)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )


@router.post('/update_category')
async def add_category(category_info: UpdateCategory, session: Session = Depends(get_session)):
    """
    新建资产、更新资产信息
    :param category_info:
    :param session:
    :return:
    """
    try:
        old_category = session.exec(
            select(assets.Category).where(assets.Category.name == category_info.category.name)).one()
        new_category = utils.update_model(old_category, category_info.category)
    except sqlalchemy.exc.NoResultFound:
        new_category = category_info.category
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    for field in category_info.fields:
        print(field)
        try:
            old_field = session.exec(select(assets.CategoryField).where(assets.CategoryField.id == field.id)).one()
            new_field = utils.update_model(old_field, field)
        except sqlalchemy.exc.NoResultFound:
            new_field = field
            new_field.category_id = new_category.id
        session.add(new_field)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
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
