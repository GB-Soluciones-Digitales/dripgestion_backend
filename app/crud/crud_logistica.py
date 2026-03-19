from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.models import logistica, cliente
from app.models.user import UserRole 
from app.models.logistica import Recorrido

def get_recorrido(db: Session, recorrido_id: int, tenant_id: int):
    return db.query(logistica.Recorrido).filter(
        logistica.Recorrido.id == recorrido_id,
        logistica.Recorrido.tenant_id == tenant_id
    ).first()

def get_recorridos_by_tenant(db: Session, tenant_id: int):
    return db.query(logistica.Recorrido).filter(logistica.Recorrido.tenant_id == tenant_id).all()

def get_recorridos_smart(db: Session, user: Any):
    if user.role != UserRole.ADMIN:
        return db.query(Recorrido).filter(
            Recorrido.tenant_id == user.tenant_id,
            Recorrido.repartidor_id == user.id
        ).all()
    
    return db.query(Recorrido).filter(Recorrido.tenant_id == user.tenant_id).all()

def create_recorrido(db: Session, recorrido_in_dict: dict, tenant_id: int):
    nuevo = logistica.Recorrido(**recorrido_in_dict, tenant_id=tenant_id)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def delete_recorrido(db: Session, recorrido: logistica.Recorrido):
    db.delete(recorrido)
    db.commit()

def create_movimiento(db: Session, mov_data: dict):
    nuevo_mov = logistica.Movimiento(**mov_data)
    db.add(nuevo_mov)
    db.commit()
    db.refresh(nuevo_mov)
    return nuevo_mov

def get_movimientos_dia(db: Session, fecha: date, tenant_id: int):
    return db.query(logistica.Movimiento, cliente.Cliente.nombre_negocio)\
        .join(cliente.Cliente)\
        .filter(
            logistica.Movimiento.tenant_id == tenant_id,
            func.date(logistica.Movimiento.fecha) == fecha
        ).order_by(logistica.Movimiento.fecha.desc()).all()

def get_movimientos_mes(db: Session, mes: int, anio: int, tenant_id: int):
    return db.query(logistica.Movimiento).filter(
        logistica.Movimiento.tenant_id == tenant_id,
        func.extract('month', logistica.Movimiento.fecha) == mes,
        func.extract('year', logistica.Movimiento.fecha) == anio
    ).all()