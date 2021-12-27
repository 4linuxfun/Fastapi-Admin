from fastapi import FastAPI, Depends
from .routers import user, menu, roles, assets, category, fields, login
from .dependencies import check_permission

app = FastAPI()

app.include_router(login.router)
app.include_router(user.router, dependencies=[Depends(check_permission)])
app.include_router(menu.router, dependencies=[Depends(check_permission)])
app.include_router(roles.router, dependencies=[Depends(check_permission)])
app.include_router(assets.router, dependencies=[Depends(check_permission)])
app.include_router(category.router, dependencies=[Depends(check_permission)])
app.include_router(fields.router, dependencies=[Depends(check_permission)])


@app.get('/')
def root():
    return {"message": "Hello world"}
