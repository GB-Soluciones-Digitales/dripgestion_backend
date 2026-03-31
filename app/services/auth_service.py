from sqlalchemy.orm import Session
from datetime import timedelta
from app.core import security
from app.core.config import settings
from app.crud import crud_user
from app.models.user import User
from app.schemas.user import PasswordUpdate

def autenticar_usuario(db: Session, username: str, password: str, tenant_id: int):
    user = crud_user.get_user_by_username(db, username=username, tenant_id=tenant_id)
    
    if not user or not security.verify_password(password, user.hashed_password):
        raise ValueError("Credenciales incorrectas para esta empresa")
        
    if not user.is_active:
        raise ValueError("Usuario inactivo")
        
    return user

def generar_token_acceso(user: User):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(user.id, user.token_version, expires_delta=access_token_expires)
    return {
        "access_token": token,
        "token_type": "bearer",
    }

def actualizar_password(db: Session, current_user: User, password_data: PasswordUpdate):
    if not security.verify_password(password_data.current_password, current_user.hashed_password):
        raise ValueError("La contraseña actual es incorrecta")
    
    nuevo_hash = security.get_password_hash(password_data.new_password)
    
    current_user.hashed_password = nuevo_hash

    current_user.token_version += 1
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user