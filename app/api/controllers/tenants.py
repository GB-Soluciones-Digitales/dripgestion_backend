from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api import deps
from app.models.user import User
from app.schemas.tenant import TenantResponse, TenantUpdate
from app.services import tenant_service

router = APIRouter()

@router.get("/info/{subdominio}", response_model=TenantResponse)
def get_tenant_info(subdominio: str, db: Session = Depends(get_db)):
    """
    Ruta pública para obtener los colores y logo de la empresa antes de iniciar sesión.
    """
    try:
        return tenant_service.obtener_info_tenant(db, subdominio)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.put("/config", response_model=TenantResponse)
def update_tenant_config(
    config_in: TenantUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Ruta privada para que el Admin actualice su empresa."""
    try:
        update_data = config_in.dict(exclude_unset=True) 
        return tenant_service.actualizar_config_tenant(db, current_user.tenant_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))