from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.schemas.producto import ProductoCreate, ProductoUpdate, ProductoResponse
from app.services import producto_service
from app.crud import crud_producto

router = APIRouter()

@router.get("", response_model=List[ProductoResponse])
def get_productos(db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    return crud_producto.get_productos_by_tenant(db, current_user.tenant_id)

@router.post("", response_model=ProductoResponse)
def create_producto(prod_in: ProductoCreate, db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    try:
        return producto_service.crear_producto(db, prod_in, current_user.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{producto_id}", response_model=ProductoResponse)
def update_precio(producto_id: int, prod_in: ProductoUpdate, db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    try:
        return producto_service.actualizar_precio_producto(db, producto_id, prod_in, current_user.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{producto_id}/toggle", response_model=ProductoResponse)
def toggle_activo(producto_id: int, db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    try:
        return producto_service.alternar_estado_producto(db, producto_id, current_user.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))