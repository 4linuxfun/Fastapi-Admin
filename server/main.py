from typing import Optional
from fastapi import FastAPI
from .routers import user, menu, roles, assets, category, fields, sysapis

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
