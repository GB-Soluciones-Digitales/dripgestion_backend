from sqlalchemy import JSON, Column, Integer, String, Float, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class CondicionIVA(str, enum.Enum):
    CONSUMIDOR_FINAL = "Consumidor Final"
    MONOTRIBUTISTA = "Monotributista"
    RESPONSABLE_INSCRIPTO = "Responsable Inscripto"
    EXENTO = "Exento"

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, index=True, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    
    # Datos de negocio
    nombre_negocio = Column(String, index=True) 
    direccion = Column(String, nullable=False)
    telefono = Column(String, nullable=True)
    observaciones = Column(String, nullable=True)

    pin_acceso = Column(String, default="0000")

    # Datos fiscales
    cuit = Column(String(11), nullable=True)
    condicion_iva = Column(Enum(CondicionIVA, native_enum=False, values_callable=lambda obj: [e.value for e in obj]), default=CondicionIVA.CONSUMIDOR_FINAL, nullable=True)
    
    # Saldos 
    saldo_dinero = Column(Float, default=0.0)
    stock_envases = Column(JSON, default={})
    
    # Logística
    orden_visita_default = Column(Integer, default=0) 

    # Relación inversa
    usuario = relationship("app.models.user.User", backref="perfil_cliente")