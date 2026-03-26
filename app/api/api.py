from fastapi import APIRouter
from app.api.controllers import auth, clientes, logistica, dashboard, productos, portal, tenants, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
api_router.include_router(logistica.router, prefix="/logistica", tags=["logistica"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(productos.router, prefix="/productos", tags=["productos"])
api_router.include_router(portal.router, prefix="/portal", tags=["portal"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Branding / Tenants"])
api_router.include_router(users.router, prefix="/users", tags=["users"])