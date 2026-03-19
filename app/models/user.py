from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.db.base import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    REPARTIDOR = "repartidor"
    CLIENTE = "cliente"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, index=True, nullable=False)
    
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    role = Column(
        Enum(UserRole, native_enum=False, values_callable=lambda obj: [e.value for e in obj]), 
        default=UserRole.REPARTIDOR
    )
    
    is_active = Column(Boolean, default=True)
    full_name = Column(String, nullable=True)