import json
from tempfile import NamedTemporaryFile
from typing import List, Optional
import pandas as pd
from fastapi import APIRouter, Depends, File, UploadFile
from starlette.background import BackgroundTask
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from ..dependencies import check_permission, base_to_json
from ..models import Assets, Category, CategoryField, ShareFields
from ..schemas import ApiResponse
from ..db import engine, get_session
from ..common import utils
from ..schemas.assets import SearchForm, UpdateAssets
from .. import crud

router = APIRouter(prefix='/api')


@router.get('/assets/count', description="查询资源的总数")
async def search_total(search: SearchForm = Depends(base_to_json), session: Session = Depends(get_session)):
    total = crud.assets.search_total(session, search)
    return ApiResponse(
        code=0,
        message="success",
        data=total
    )


@router.get('/assets/category/fields', description="查找资产可查询字段")
async def get_category_field(category_id: int, query: Optional[str] = None, session: Session = Depends(get_session)):
    search = select(CategoryField).where(CategoryField.category_id == category_id)
    if query is not None:
        print('query is not none' + query)
        search = search.where(CategoryField.name.like('%' + query + '%'))
    fields = session.exec(search).all()
    print(fields)
    return ApiResponse(
        code=0,
        message="success",
        data=fields
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
        static_dict = {value: key for key, value in ShareFields.share_names().items()}
        static_list = static_dict.keys()
        dynamic_list = list(set(col_list) - set(static_list))
        print(dynamic_list)
        dynamic_data = df[dynamic_list]
        print(dynamic_data)
        # 静态字段统一修改中文为英文（数据库表字段为英文）
        df.rename(
            columns=static_dict, inplace=True)
        category = df['category'].iloc[0]
        category = session.exec(select(Category).where(Category.name == category)).one()
        datetime_fields = session.exec(
            select(CategoryField).where(CategoryField.category_id == category.id).where(
                CategoryField.type.like('date%'))).all()
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
    category = session.exec(select(Category).where(Category.id == id)).one()
    print(ShareFields.share_names().values())
    excel_title = []
    excel_title.extend(ShareFields.share_names().values())
    for field in category.fields:
        excel_title.append(field.name)
    output_data = pd.DataFrame(columns=[excel_title])
    # return FileResponse('server/static/template/system.xlsx', filename='system.xlsx')
    with NamedTemporaryFile('w+b', suffix='.xlsx', delete=False) as f:
        # output_data.set_index('资产类型', inplace=True)
        output_data.to_excel(f, index=False)
        return FileResponse(f.name, filename='template.xlsx', background=BackgroundTask(utils.remove_tmp_file, f.name))


@router.put('/assets/multi', description="批量更新资产信息", dependencies=[Depends(check_permission), ])
async def update_assets(update: UpdateAssets, session: Session = Depends(get_session)):
    print(update)
    assets_result = session.exec(select(Assets).where(Assets.id.in_(update.assets)))
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


@router.put('/assets', description="更新资产", dependencies=[Depends(check_permission), ])
async def update_category_detail(new_asset: Assets, session: Session = Depends(get_session)):
    old_asset = session.exec(select(Assets).where(Assets.id == new_asset.id)).one()
    old_asset = utils.update_model(old_asset, new_asset)
    session.add(old_asset)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )


@router.get('/assets', description="搜索资源")
def search_system(search: SearchForm = Depends(base_to_json), session: Session = Depends(get_session)):
    print(search)
    if not search.category:
        return ApiResponse(
            code=1,
            message="error",
            data='请选择资产类型'
        )
    results = crud.assets.search_assets(session, search)
    assets = []
    for asset in results:
        tmp = asset.dict().copy()
        info = tmp['info'].copy()
        del tmp['info']
        tmp.update(info)
        print(tmp)
        assets.append(tmp)

    print(assets)
    return ApiResponse(
        code=0,
        message="success",
        data=assets
    )


@router.post('/assets', description="手动添加资产", dependencies=[Depends(check_permission), ])
async def add_asset(asset: Assets, session: Session = Depends(get_session)):
    print(asset)
    session.add(asset)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )


@router.post("/system/output")
def output_data(system: SearchForm, session: Session = Depends(get_session)):
    sql = make_search_sql(system)
    df = pd.read_sql_query(sql, session.bind)
    static_dict = ShareFields.share_names()
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
