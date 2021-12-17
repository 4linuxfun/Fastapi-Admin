from typing import Optional
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..dependencies import get_session, check_permission
from ..sql.models import CategoryField
from ..sql.schemas import ApiResponse

router = APIRouter(prefix='/api', dependencies=[Depends(check_permission), ])


@router.get('/fields', description="返回对应资产的字段列表")
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
