from sqlalchemy.orm import Session
from app.crud import crud_user
from app.schemas.user import UserCreate, UserUpdate
from fastapi import HTTPException, status

def crear_nuevo_usuario(db: Session, user_in: UserCreate, tenant_id: int):
    user_existente = crud_user.get_user_by_username(db, user_in.username, tenant_id)
    if user_existente:
        raise ValueError("El nombre de usuario ya está registrado en esta empresa.")
    
    return crud_user.create_user_within_tenant(db, user_in, tenant_id)

def listar_usuarios(db: Session, tenant_id: int):
    return crud_user.get_users_by_tenant(db, tenant_id)

def actualizar_usuario(db: Session, user_id: int, user_in: UserUpdate, tenant_id: int):
    user_existente = crud_user.get_user_by_username(db, user_in.username, tenant_id)
    if user_existente and user_existente.id != user_id:
        raise ValueError("El nombre de usuario ya está siendo usado por otro miembro.")
    
    user_actualizado = crud_user.update_user_within_tenant(db, user_id, user_in, tenant_id)
    if not user_actualizado:
        raise ValueError("Usuario no encontrado o no pertenece a la empresa.")
        
    return user_actualizado

def eliminar_usuario(db: Session, user_id: int, tenant_id: int):
    user = crud_user.delete_user(db, user_id, tenant_id)
    if not user:
        raise ValueError("El usuario no existe o no pertenece a tu empresa.")
    return user