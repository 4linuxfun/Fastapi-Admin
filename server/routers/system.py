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
    filters: Optional[list]


class UpdateCategory(BaseModel):
    category: assets.Category
    fields: List[assets.CategoryField]


class UpdateAssets(BaseModel):
    # 批量更新资产信息提交内容
    assets: List[int]
    update: List[Dict[str, Any]]


@router.post('/system/search_total')
async def search_total(system: SearchForm, session: Session = Depends(get_session)):
    sql = make_search_sql(system, model='count')
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
    sql = make_search_sql(system)
    sql = sql.offset(system.offset).limit(system.limit)
    print(str(sql))
    results = session.exec(sql).all()

    print(results)
    return ApiResponse(
        code=0,
        message="success",
        data=results
    )


@router.post('/system/import', description="批量数据的导入")
def data_import(files: List[UploadFile] = File(...), session: Session = Depends(get_session)):
    """
    每个导入的文件，都存在静态字段、动态字段，需要对动态字段转换成json格式的字符串，然后才能进行插入
    :param files: files参数是前后端统一规定的名字，如果需要修改，同意修改
    :param session:
    :return:
    """
    for file in files:
        print(file.filename)
        contents = file.file.read()
        df = pd.read_excel(contents, engine='openpyxl', keep_default_na=False)
        print(df)
        # 使用此种方式去过滤掉未设置列名的列
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        print(df)
        col_list = df.columns.values.tolist()
        print(col_list)
        # 需要做一次中英文翻转
        static_dict = {value: key for key, value in assets.ShareFields.share_names().items()}
        static_list = static_dict.keys()
        dynamic_list = list(set(col_list) - set(static_list))
        print(dynamic_list)
        dynamic_data = df[dynamic_list]
        print(dynamic_data)
        # 静态字段统一修改中文为英文（数据库表字段为英文）
        df.rename(
            columns=static_dict, inplace=True)
        category = df['category'].iloc[0]
        category = session.exec(select(assets.Category).where(assets.Category.name == category)).one()
        datetime_fields = session.exec(
            select(assets.CategoryField).where(assets.CategoryField.category_id == category.id).where(
                assets.CategoryField.type.like('date%'))).all()
        for field in datetime_fields:
            if field.type == 'date':
                date_format = '%Y-%m-%d'
            elif field.type == 'datetime':
                date_format = '%Y-%m-%d HH:MM:SS'
            df[field.name] = df[field.name].dt.strftime(date_format)
        print(category)
        print(df)
        df['info'] = df.apply(to_json, axis=1, args=(dynamic_list,))

        df.drop(columns=dynamic_list, inplace=True)
        print(df)
        df.to_sql('assets', engine, if_exists='append', index=False, method='multi')
    return ApiResponse(
        code=0,
        message="success",
    )


@router.get('/system/down_temp/{id}', description="导入模板下载")
def download_tmpfile(id: int, session: Session = Depends(get_session)):
    category = session.exec(select(assets.Category).where(assets.Category.id == id)).one()
    print(assets.ShareFields.share_names().values())
    excel_title = []
    excel_title.extend(assets.ShareFields.share_names().values())
    for field in category.fields:
        excel_title.append(field.name)
    output_data = pd.DataFrame(columns=[excel_title])
    # return FileResponse('server/static/template/system.xlsx', filename='system.xlsx')
    with NamedTemporaryFile('w+b', suffix='.xlsx', delete=False) as f:
        # output_data.set_index('资产类型', inplace=True)
        output_data.to_excel(f, index=False)
        return FileResponse(f.name, filename='template.xlsx', background=BackgroundTask(utils.remove_tmp_file, f.name))


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


@router.get('/category_field')
async def get_category_field(category_id: int, query: Optional[str] = None, session: Session = Depends(get_session)):
    search = select(assets.CategoryField).where(assets.CategoryField.category_id == category_id)
    if query is not None:
        print('query is not none' + query)
        search = search.where(assets.CategoryField.name.like('%' + query + '%'))
    fields = session.exec(search).all()
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


@router.post('/add', description="手动添加资产")
async def add_asset(asset: assets.Assets, session: Session = Depends(get_session)):
    print(asset)
    session.add(asset)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
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
    sql = make_search_sql(system)
    df = pd.read_sql_query(sql, session.bind)
    static_dict = assets.ShareFields.share_names()
    # 静态字段统一修改中文为英文（数据库表字段为英文）
    df.rename(
        columns=static_dict, inplace=True)
    df.drop(columns=['id'], inplace=True)
    # df['info'] = df.apply(to_column, axis=1, args=(dynamic_list,))
    info = pd.json_normalize(df['info'])
    print(info)
    result = pd.concat([df, info], axis=1)
    result.drop(columns=['info', 'deleted'], inplace=True)
    print(result)
    with NamedTemporaryFile('w+b', suffix='.xlsx', delete=False) as f:
        result.to_excel(f, index=False)
        return FileResponse(f.name, filename='output.xlsx', background=BackgroundTask(utils.remove_tmp_file, f.name))


def to_json(x, dynamic_list):
    """
    dataframe的column合并成json字段
    :param x:
    :param dynamic_list:
    :return:
    """
    print(x)
    info = {}
    for value in dynamic_list:
        info[value] = x[value]
    return json.dumps(info)


def make_search_sql(search: SearchForm, model='all'):
    """
    searchForm生成对应的查询sql
    :param search:
    :param model: 'all':代表查询所有，'count':表示返回count
    :return:
    """
    if model == 'all':
        sql = select(assets.Assets)
    elif model == 'count':
        sql = select(func.count(assets.Assets.id))
    if search.category:
        sql = sql.where(assets.Assets.category.like('%' + search.category + '%'))
    if search.manager:
        sql = sql.where(assets.Assets.manager.like('%' + search.manager + '%'))
    if search.area:
        sql = sql.where(assets.Assets.area.like('%' + search.area + '%'))
    if search.user:
        sql = sql.where(assets.Assets.user.like('%' + search.user + '%'))
    for key, value in search.info.items():
        if value:
            sql = sql.where(assets.Assets.info[key].like('%' + value + '%'))
    if search.filters is not None:
        for filter in search.filters:
            print(filter)
            if filter['field'] is None:
                continue
            if filter['type'] == 'like':
                sql = sql.where(assets.Assets.info[filter['field']].like('%' + filter['value'] + '%'))
            if filter['type'] == 'eq':
                sql = sql.where(assets.Assets.info[filter['field']] == filter['value'])
            if filter['type'] == 'lt':
                sql = sql.where(assets.Assets.info[filter['field']] < filter['value'])
            if filter['type'] == 'le':
                sql = sql.where(assets.Assets.info[filter['field']] <= filter['value'])
            if filter['type'] == 'gt':
                sql = sql.where(assets.Assets.info[filter['field']] > filter['value'])
            if filter['type'] == 'ge':
                sql = sql.where(assets.Assets.info[filter['field']] >= filter['value'])
            if filter['type'] == 'ne':
                sql = sql.where(assets.Assets.info[filter['field']] != filter['value'])
    return sql
