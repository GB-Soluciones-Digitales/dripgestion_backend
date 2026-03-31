from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api import deps
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.tenant import TenantResponse, TenantUpdate
from app.services import tenant_service
from app.services import cloudinary_service

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
MAGIC_NUMBERS = {
    "png": b"\x89PNG\r\n\x1a\n",
    "jpeg": b"\xff\xd8\xff",
    "jpg": b"\xff\xd8\xff",
}

router = APIRouter()

@router.get("/info/{subdominio}", response_model=TenantResponse)
def get_tenant_info(subdominio: str, db: Session = Depends(get_db)):
    try:
        return tenant_service.obtener_info_tenant(db, subdominio)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.put("/config", response_model=TenantResponse)
def update_tenant_config(config_in: TenantUpdate, db: Session = Depends(get_db), current_admin: User = Depends(deps.get_current_admin)):
    try:
        update_data = config_in.dict(exclude_unset=True) 
        return tenant_service.actualizar_config_tenant(db, current_admin.tenant_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.post("/config/logo")
async def upload_tenant_logo(file: UploadFile = File(...), db: Session = Depends(get_db), current_admin: User = Depends(deps.get_current_admin)):

    file.file.seek(0, 2) 
    file_size = file.file.tell() 
    await file.seek(0) 
    
    if file_size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="El archivo es demasiado grande. Máximo 5MB.")
    
    header = await file.read(20)
    await file.seek(0) 
    
    is_valid_image = any(header.startswith(magic) for magic in MAGIC_NUMBERS.values())
    
    if not is_valid_image:
        raise HTTPException(status_code=400, detail="Formato de imagen no válido o archivo corrupto. Solo JPG/PNG.")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen (PNG, JPG, etc.)")

    tenant = db.query(Tenant).filter(Tenant.id == current_admin.tenant_id).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    try:
        upload_result = cloudinary_service.subir_logo(file, current_admin.tenant_id, tenant.logo_public_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al subir la imagen a la nube")

    tenant.logo_url = upload_result["logo_url"]
    tenant.logo_public_id = upload_result["logo_public_id"]
    
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    return {
        "message": "Logo actualizado correctamente", 
        "logo_url": tenant.logo_url
    }