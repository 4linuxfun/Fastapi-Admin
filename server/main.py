from sqlmodel import Session
from fastapi import FastAPI, Depends
from .routers import user, menu, roles, assets, category, login, form
from .dependencies import check_permission
from .models import Api
from .db import engine, get_or_create

app = FastAPI()

# 不执行check_permission的，表示不需要权限验证
app.include_router(login.router, tags=['用户登录'])
# app.include_router(form.router)
app.include_router(user.router, tags=['用户管理'], dependencies=[Depends(check_permission)])
app.include_router(menu.router, tags=['菜单管理'], dependencies=[Depends(check_permission)])
app.include_router(roles.router, tags=['角色管理'], dependencies=[Depends(check_permission)])
app.include_router(assets.router, tags=['资产管理'], dependencies=[Depends(check_permission)])
app.include_router(category.router, tags=['类别管理'], dependencies=[Depends(check_permission)])


@app.on_event("startup")
def startup():
    """
    在此时添加openapi数据的获取，导入api表，判断有没有新接口信息需要添加进去
    :return:
    """
    print('服务启动后执行服务')
    with Session(engine) as session:
        for url, value in app.openapi()['paths'].items():
            print(url)
            if 'get' in value:
                method = 'get'
            if 'post' in value:
                method = 'post'
            if 'put' in value:
                method = 'put'
            if 'delete' in value:
                method = 'delete'
            print(value)
            print(value[method]['tags'])
            tags = value[method]['tags'][0]
            get_or_create(session, Api, tags=tags, path=url, method=method, summary=value[method]['summary'])


@app.on_event("shutdown")
def shutdown():
    print('关闭服务')
