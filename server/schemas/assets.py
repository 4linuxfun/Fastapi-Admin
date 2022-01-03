from typing import Optional, List, Any,Dict
from pydantic import BaseModel
from ..sql.models import Assets


class SearchForm(Assets):
    limit: Optional[int]
    offset: Optional[int]
    filters: Optional[list]


class UpdateAssets(BaseModel):
    # 批量更新资产信息提交内容
    assets: List[int]
    update: List[Dict[str, Any]]
