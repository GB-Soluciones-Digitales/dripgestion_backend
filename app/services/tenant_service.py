from sqlalchemy.orm import Session
from app.crud import crud_tenant

def obtener_info_tenant(db: Session, subdominio: str):
    tenant = crud_tenant.get_tenant_by_subdomain(db, subdominio)
    if not tenant:
        raise ValueError("Empresa no encontrada o inactiva")
    return tenant

def actualizar_config_tenant(db: Session, tenant_id: int, config_in: dict):
    tenant = crud_tenant.get_tenant_by_id(db, tenant_id)
    if not tenant:
        raise ValueError("Empresa no encontrada")
    
    return crud_tenant.update_tenant(db, tenant, config_in)