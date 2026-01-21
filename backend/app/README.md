服务启动

uvicorn app.main:app --reload

## 知识点介绍

### 带参数分页查询

#### Pagination 定义

```python
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')


class Pagination(BaseModel, Generic[T]):
    search: T
    page: Optional[int] = 1
    page_size: Optional[int] = 10
    model: Optional[str] = 'asc'
```

#### ApiSearch 定义

```python
from typing import Dict
from ...models.internal.api import ApiBase


class ApiSearch(ApiBase):
    type: Dict[str, str]
```

#### ApiBase 为数据库字段的定义

```python
class ApiBase(SQLModel):
    tags: str
    path: str
    method: str
    summary: str
    deprecated: int = Field(default=0)
```

#### 解析分页查询请求

```python
#引入Pagination
from ...schemas.internal.pagination import Pagination

#定义POST请求，并解析，其中ApiSearch为定义的Pagination.search字段解析
@router.post('/sysapis', summary='获取API列表')
async def get_sysapis(search: Pagination[ApiSearch],
                      session: Session = Depends(get_session)):
    print(search)
    total = crud.internal.api.search_total(session, search.search)
    print(total)
    sys_apis = crud.internal.api.search(session, search)
    return {
        'total': total,
        'data': sys_apis
    }
```
