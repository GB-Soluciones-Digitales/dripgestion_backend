from typing import Optional
from pydantic import BaseModel

class TenantBase(BaseModel):
    nombre: str
    subdominio: str
    whatsapp: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True
    font_sans: Optional[str] = "'Inter', sans-serif"
    color_primario: Optional[str] = "#25A7DA"
    color_primario_light: Optional[str] = "#00ACC1"
    color_primario_dark: Optional[str] = "#0C4A6E"
    color_background: Optional[str] = "#F0FDFA"
    color_success: Optional[str] = "#10b981"
    color_danger: Optional[str] = "#ef4444"
    color_secondary: Optional[str] = "#64748b"

class TenantCreate(TenantBase):
    nombre: Optional[str] = None
    subdominio: Optional[str] = None
    whatsapp: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None
    font_sans: Optional[str] = None
    color_primario: Optional[str] = None
    color_primario_light: Optional[str] = None
    color_primario_dark: Optional[str] = None
    color_background: Optional[str] = None
    color_success: Optional[str] = None
    color_danger: Optional[str] = None
    color_secondary: Optional[str] = None

class TenantUpdate(BaseModel):
    nombre: Optional[str] = None
    whatsapp: Optional[str] = None
    logo_url: Optional[str] = None
    font_sans: Optional[str] = None
    color_primario: Optional[str] = None
    color_primario_light: Optional[str] = None
    color_primario_dark: Optional[str] = None
    color_background: Optional[str] = None
    color_success: Optional[str] = None
    color_danger: Optional[str] = None
    color_secondary: Optional[str] = None

class TenantResponse(TenantBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True