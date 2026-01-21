# Assets module main router
from fastapi import APIRouter
from .assets import router as assets_router
from .categories import router as categories_router
from .locations import router as locations_router
from .departments import router as departments_router
from .inventory import router as inventory_router

# 创建主路由，统一设置前缀
router = APIRouter(prefix="/api/assets")

# 包含所有子路由
router.include_router(assets_router)
router.include_router(categories_router)
router.include_router(locations_router)
router.include_router(departments_router)
router.include_router(inventory_router)

__all__ = ["router"]
