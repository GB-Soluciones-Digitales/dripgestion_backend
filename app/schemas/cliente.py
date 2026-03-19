from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from app.models.cliente import CondicionIVA

class ClienteBase(BaseModel):
    nombre_negocio: str
    direccion: str
    telefono: Optional[str] = None
    cuit: Optional[str] = None
    condicion_iva: Optional[CondicionIVA] = CondicionIVA.CONSUMIDOR_FINAL
    observaciones: Optional[str] = None
    
class ClienteCreate(ClienteBase):
    pin_acceso: str = "1234" 

class ClienteUpdate(BaseModel):
    nombre_negocio: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    observaciones: Optional[str] = None
    pin_acceso: Optional[str] = None
    cuit: Optional[str] = None
    condicion_iva: Optional[CondicionIVA] = CondicionIVA.CONSUMIDOR_FINAL

class ClienteResponse(ClienteBase):
    id: int
    tenant_id: int
    saldo_dinero: float
    stock_envases: Dict[str, Any] = {}
    orden_visita_default: int
    pin_acceso: str

    class Config:
        from_attributes = True