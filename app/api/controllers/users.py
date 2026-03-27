from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.services import user_service
from app.db.session import get_db

router = APIRouter()

@router.get("", response_model=List[schemas.user.UserResponse])
def get_usuarios_equipo(db: Session = Depends(get_db), current_admin: models.user.User = Depends(deps.get_current_admin)):
    return user_service.listar_usuarios(db, current_admin.tenant_id)

@router.get("/{user_id}", response_model=schemas.user.UserResponse)
def obtener_usuario_detalle(user_id: int, db: Session = Depends(get_db), current_admin: models.user.User = Depends(deps.get_current_admin)):
    user = user_service.obtener_por_id(db, user_id, current_admin.tenant_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.post("", response_model=schemas.user.UserResponse)
def crear_usuario_equipo(user_in: schemas.user.UserCreate, db: Session = Depends(get_db), current_admin: models.user.User = Depends(deps.get_current_admin)):
    try:
        return user_service.crear_nuevo_usuario(db, user_in, current_admin.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.put("/{user_id}", response_model=schemas.user.UserResponse)
def editar_usuario_equipo(
    user_id: int, 
    user_in: schemas.user.UserUpdate, 
    db: Session = Depends(get_db), 
    current_admin: models.user.User = Depends(deps.get_current_admin)
):
    try:
        return user_service.actualizar_usuario(db, user_id, user_in, current_admin.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{user_id}")
def eliminar_usuario_equipo(user_id: int, db: Session = Depends(get_db), current_admin: models.user.User = Depends(deps.get_current_admin)):
    try:
        user_service.eliminar_usuario(db, user_id, current_admin.tenant_id)
        return {"message": "Usuario eliminado correctamente"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))