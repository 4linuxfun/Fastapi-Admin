# Fastapi Admin

前后端分离项目实现的一个后端管理框架

* 前端：vue3 + element plus
* 后端：fastapi + sqlmodel
* 任务管理: rpyc+apscheduler

**个人学习项目，只会对明显的bug进行修复，不会进行过多新功能的更新**

常用分支说明：

* main：主分支，所有功能都会往这里合并
* test： 测试分支

## 测试环境服务启动

1. nginx添加配置：

```
 server {
        listen       80;
        server_name  localhost;

        #charset koi8-r;

        #access_log  logs/host.access.log  main;

        location / {
        proxy_pass http://127.0.0.1:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

		# api
		location /api/ {
			proxy_pass http://127.0.0.1:8000;
			client_max_body_size 100m;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
			#proxy_pass http://127.0.0.1:4523/mock/412521/api/;
		}
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }


    }

```

## 生产环境部署

1. 前端执行打包命令

```
npm run build
```

2. 添加nginx配置

```
server {
        listen 80;
        location / {
                root /opt/www; #打包后前端放置目录
                index index.html;
                try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://127.0.0.1:8000;
            client_max_body_size 100m;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
                        #proxy_pass http://127.0.0.1:4523/mock/412521/api/;
                }
}
```

## 服务管理

* dev:开发环境，使用uvicorn启动
* pro:生产环境，使用gunicorn启动

```
./service.sh {dev|pro} {start|stop|restart}
```
后端需要修改对应配置文件信息
* dev: config/development.yaml
* pro: config/production.yaml

开发模式下，uvicorn服务能自动刷新，rpyc服务无法自动刷新，需要手动重启

## 约束

1. 后端数据库对于布尔值的传递统一数据库设置为tinyint，0为假，1为真
2. 前端所有bool都0为假，1为真

# 功能实现介绍

## 分页查询实现

### 前端

```js
<!-- 导入分页相关方法 -->
import usePagination from '@/composables/usePagination'

<
!--定义一个搜索字段-- >
const searchForm = {
    name: null,
    email: null,
    enable: null
}

<!-- 传入查询相关字段信息 -->
const {
    search,
    tableData,
    currentPage,
    pageSize,
    orderModel,
    total,
    freshCurrentPage,
    handleSearch
} = usePagination('/api/users/search', searchForm)
```

### 后端

定义了一个分页模型

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

使用

```python
@router.post('/dict/item/search', summary="字典列表查询", response_model=ApiResponse[SearchResponse[DictRead]])
async def search_items(search: Pagination[DictItemSearch], session: Session = Depends(get_session)):
    # 需要定义一个filter_type，用于区分各个字段的匹配形式，可用为：l_like、r_like、like、eq、ne、lt、le、gt、ge
    filter_type = DictItemSearchFilter(dict_id='eq', label='like', enable='eq', value='like')
    total = crud.internal.dict_item.search_total(session, search.search, filter_type.model_dump())
    items: List[DictRead] = crud.internal.dict_item.search(session, search, filter_type.model_dump())
    # 转义下数据类型，不然在执行return的时候，会去获取外键、关联字段相关的内容，容易造成数据量过多等问题
    item_list = [DictRead.from_orm(item) for item in items]
    return ApiResponse(
        data={
            'total': total,
            'data': item_list
        }

    )
```

## 权限管控

通过casbin实现简化的权限管控功能，思路如下：

1. 对于不需要token验证的，写入settings的APISettings.NO_VERIFY_URL中
2. 对于需要权限管控的接口，写入casbin中，并且对需要权限验证的接口使用casbin验证
3. 前端通过权限字段，进行显示
4. 只能对按钮级别的功能实现权限管控
5. 页面管控，只是后端返回菜单列表，前端根据菜单列表进行显示，后端没有对页面进行权限管控

### 前端

v-permission定义了权限标识，当拥有权限时，可以页面上能显示按钮，同时，后端也会进行权限的判断。

```js
   <el-button v-permission="'role:update'" v-if="scope.row.name!='admin'" type="primary" size="small"
                     @click = "handleEdit(scope.row)" > 编辑
    < /el-button>
```

### 后端

```python
@router.put('/roles', summary="更新角色", response_model=ApiResponse[Role],
            dependencies=[Depends(Authority('role:update'))])
async def update_roles(role_info: RoleUpdate, session: Session = Depends(get_session)):
    print(role_info)
    if role_info.name == 'admin':
        ApiResponse(code=status.HTTP_400_BAD_REQUEST, message='admin权限组无法更新信息')
    db_obj = crud.internal.role.get(session, role_info.id)
    enable_menus = role_info.menus
    delattr(role_info, 'menus')
    db_obj = crud.internal.role.update(session, db_obj, role_info)
    crud.internal.role.update_menus(session, db_obj, enable_menus)
    return ApiResponse(
        data=db_obj
    )
```

## 项目截图

### 系统登录

![登录页面](./images/login.png)

### 用户管理

![用户管理页面](./images/user.png)
![添加新用户](./images/user_add.png)

### 角色管理

![角色管理页面](./images/role.png)
![添加新角色](./images/role_add.png)

### 菜单管理

![菜单管理页面](./images/menu.png)
![添加新菜单](./images/menu_add.png)

### 数据字典管理

![数据字典管理](./images/dictonary.png)
![数据字典元素管理](./images/dictonary_items.png)

### 任务管理

![任务管理](./images/job_manage.png)
![脚本管理](./images/job_playbook.png)

### 参考项目：

* https://github.com/xingxingzaixian/FastAPI-MySQL-Tortoise-Casbin