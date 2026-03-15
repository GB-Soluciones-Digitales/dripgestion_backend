from sqlalchemy.orm import Session
from app.models.tenant import Tenant

def get_tenant_by_subdomain(db: Session, subdominio: str):
    return db.query(Tenant).filter(
        Tenant.subdominio == subdominio, 
        Tenant.is_active == True
    ).first()

def get_tenant_by_id(db: Session, tenant_id: int):
    return db.query(Tenant).filter(
        Tenant.id == tenant_id, 
        Tenant.is_active == True
    ).first()

def update_tenant(db: Session, db_obj: Tenant, obj_in: dict):
    for field, value in obj_in.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj