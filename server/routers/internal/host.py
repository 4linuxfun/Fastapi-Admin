from typing import Optional, List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from server.models.internal.host import CreateGroup
from ...common.response_code import ApiResponse, SearchResponse
from ...common.database import get_session
from ... import crud

router = APIRouter(prefix='/api')


@router.post('/host/group', summary='添加主机分组')
async def create_group(group: CreateGroup, session: Session = Depends(get_session)):
    crud.internal.group.insert(session, group)
    return ApiResponse()
