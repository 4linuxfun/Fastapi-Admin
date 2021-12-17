from typing import Optional
from fastapi import FastAPI, Depends
from .routers import user, menu, roles, assets, category, fields, sysapis
from .dependencies import check_permission

app = FastAPI()

app.include_router(user.router)
app.include_router(menu.router)
app.include_router(roles.router)
app.include_router(assets.router)
app.include_router(category.router)
app.include_router(fields.router)
app.include_router(sysapis.router)


@app.get('/')
def root():
    return {"message": "Hello world"}
