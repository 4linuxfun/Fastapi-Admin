from typing import Optional, List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from ...schemas.internal.pagination import Pagination
from ...models.internal.dictonary import DataDict, DictRead, DictBase, DictUpdate, DictItem
from ...schemas.internal.dictonary import DictSearch, DictItemSearch
from ...common.response_code import ApiResponse, SearchResponse
from ...common.database import get_session
from ... import crud

router = APIRouter(prefix='/api')


@router.post('/dict/item/search', summary="字典列表查询", response_model=ApiResponse[SearchResponse[DictRead]])
async def search_items(search: Pagination[DictItemSearch], session: Session = Depends(get_session)):
    total = crud.internal.dict_item.search_total(session, search.search)
    items: List[DictRead] = crud.internal.dict_item.search(session, search)
    item_list = [DictRead.from_orm(item) for item in items]
    return ApiResponse(
        data={
            'total': total,
            'data': item_list
        }

    )


@router.post('/dict/item', summary="添加字典字段", response_model=ApiResponse[DictRead])
async def add_dict_item(dict_item: DictUpdate, session: Session = Depends(get_session)):
    new_item = crud.internal.dict_item.insert(session, DictItem(**dict_item.dict()))
    return ApiResponse(
        data=DictRead.from_orm(new_item)
    )


@router.put('/dict/item', summary="更新字典元素", response_model=ApiResponse)
async def update_dict_item(dict_item: DictUpdate, session: Session = Depends(get_session)):
    db_obj = crud.internal.dict_item.get(session, dict_item.id)
    crud.internal.dict_item.update(session, db_obj, dict_item)
    return ApiResponse()


@router.delete('/dict/item/{item_id}', summary="删除字典元素", )
async def del_dict_item(item_id: int, session: Session = Depends(get_session)):
    crud.internal.dict_item.delete(session, item_id)
    return ApiResponse()


@router.post("/dict", summary="新建数据字典", response_model=ApiResponse[DataDict])
async def add_dict(data_dict: DataDict, session: Session = Depends(get_session)):
    obj = crud.internal.data_dict.insert(session, data_dict)
    return ApiResponse(
        data=obj
    )


@router.post('/dict/search',
             summary="查询数据字典")
async def get_dicts(search: Pagination[DictSearch], session: Session = Depends(get_session)):
    total = crud.internal.data_dict.search_total(session, search.search)
    dicts: List[DataDict] = crud.internal.data_dict.search(session, search)
    return ApiResponse(
        data={
            'total': total,
            'data': dicts
        }
    )
