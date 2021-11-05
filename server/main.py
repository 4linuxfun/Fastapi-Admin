from typing import Optional
from fastapi import FastAPI
from .routers import user, menu, roles, system

app = FastAPI()

app.include_router(user.router)
app.include_router(menu.router)
app.include_router(roles.router)
app.include_router(system.router)


@app.get('/')
def root():
    return {"message": "Hello world"}
