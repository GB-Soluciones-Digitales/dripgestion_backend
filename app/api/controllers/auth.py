from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Header, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas, models
from app.api import deps
from app.db.session import get_db
from app.schemas.user import UserResponse
from app.services import auth_service
from app.core.limiter import limiter

router = APIRouter()

@router.post("/login/access-token", response_model=schemas.Token)
@limiter.limit("5/minute")
def login_access_token(request: Request, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends(), x_tenant_id: int = Header(..., alias="X-Tenant-ID")) -> Any:
    try:
        user = auth_service.autenticar_usuario(db, form_data.username, form_data.password, x_tenant_id)
        return auth_service.generar_token_acceso(user)
    except ValueError as e:
        status_code = status.HTTP_400_BAD_REQUEST if "inactivo" in str(e) else status.HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=status_code, detail=str(e))

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: models.user.User = Depends(deps.get_current_user)):
    return current_user

@router.post("/me/logout-all", status_code=status.HTTP_200_OK)
def logout_all_devices(db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    current_user.token_version += 1
    
    db.add(current_user)
    db.commit()
    
    return {"message": "Sesión cerrada en todos los dispositivos exitosamente."}

@router.put("/password", status_code=status.HTTP_200_OK)
def update_user_password(password_data: schemas.user.PasswordUpdate, db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    try:
        auth_service.actualizar_password(db, current_user, password_data)
        return {"message": "Contraseña actualizada exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))