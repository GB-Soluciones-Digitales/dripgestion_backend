from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    subdominio = Column(String, unique=True, index=True, nullable=False)
    whatsapp = Column(String, nullable=True)
    
    # --- Branding Dinámico ---
    logo_url = Column(String, nullable=True)
    logo_public_id = Column(String, nullable=True)
    font_sans = Column(String, default="'Inter', sans-serif")
    color_primario = Column(String, default="#25A7DA")
    color_primario_light = Column(String, default="#00ACC1")
    color_primario_dark = Column(String, default="#0C4A6E")
    color_background = Column(String, default="#F0FDFA")
    color_success = Column(String, default="#10b981")
    color_danger = Column(String, default="#ef4444")
    color_secondary = Column(String, default="#64748b")
    
    is_active = Column(Boolean, default=True)