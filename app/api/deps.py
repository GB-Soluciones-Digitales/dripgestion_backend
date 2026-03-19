from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal, get_db

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login/access-token"
)

def get_db_session() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> models.user.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.token.TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se pudo validar las credenciales",
        )
        
    user = db.query(models.user.User).filter(models.user.User.id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return user

def get_current_admin(
    current_user: models.user.User = Depends(get_current_user)
) -> models.user.User:
    if current_user.role != models.user.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene privilegios de administrador",
        )
    return current_user