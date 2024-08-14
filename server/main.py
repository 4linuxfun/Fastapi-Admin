from fastapi import FastAPI, Depends
from loguru import logger
from .common.log import init_logging
from .routers.internal import login, user, menu, roles, dictonary, job, host, playbook
from .common.security import auth_check

init_logging()

app = FastAPI(dependencies=[Depends(auth_check)])

app.include_router(login.router, tags=['用户登录'])
app.include_router(user.router, tags=['用户管理'])
app.include_router(menu.router, tags=['菜单管理'])
app.include_router(roles.router, tags=['角色管理'])
app.include_router(dictonary.router, tags=['数据字典'])
app.include_router(job.router, tags=['任务管理'])
app.include_router(host.router, tags=['主机管理'])
app.include_router(playbook.router, tags=['playbook管理'])


@app.on_event("startup")
async def startup():
    """
    在此时添加openapi数据的获取，导入api表，判断有没有新接口信息需要添加进去
    :return:
    """
    logger.debug('服务启动后执行服务')


@app.on_event("shutdown")
def shutdown():
    logger.debug('关闭服务')
