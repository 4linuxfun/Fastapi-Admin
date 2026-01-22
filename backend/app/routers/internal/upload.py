from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional, List
from app.common.utils import upload_files
from app.settings import settings
from app.common.response_code import ApiResponse


router = APIRouter(prefix="/api")


@router.post("/upload", summary="上传文件")
async def upload_file(
    file: List[UploadFile] = File(...), tag: Optional[str] = Form("common")
):
    """
    通用文件上传接口
    :param file: 文件对象列表
    :param tag: 分类标签，默认为 'common'
    :return: 文件访问URL
    """
    # upload_files expects a list of files
    urls = await upload_files(file, settings.upload_dir, tag)
    result_data = {"urls": urls}
    return ApiResponse(data=result_data)
