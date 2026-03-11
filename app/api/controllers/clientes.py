from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.services import cliente_service

router = APIRouter()

@router.get("", response_model=List[schemas.ClienteResponse])
def read_clientes(db: Session = Depends(get_db), skip: int = 0, limit: int = 100, current_user: models.user.User = Depends(deps.get_current_user)):
    return db.query(models.cliente.Cliente).filter(models.cliente.Cliente.tenant_id == current_user.tenant_id).offset(skip).limit(limit).all()

@router.post("", response_model=schemas.ClienteResponse)
def create_cliente(cliente_in: schemas.ClienteCreate, db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    try:
        return cliente_service.crear_cliente_y_usuario(db, cliente_in, current_user.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{cliente_id}", response_model=schemas.ClienteResponse)
def read_cliente_by_id(cliente_id: int, db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    cliente = db.query(models.cliente.Cliente).filter(models.cliente.Cliente.id == cliente_id, models.cliente.Cliente.tenant_id == current_user.tenant_id).first()
    if not cliente: raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@router.put("/{cliente_id}", response_model=schemas.ClienteResponse)
def update_cliente(cliente_id: int, cliente_in: schemas.ClienteUpdate, db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    cliente = db.query(models.cliente.Cliente).filter(models.cliente.Cliente.id == cliente_id, models.cliente.Cliente.tenant_id == current_user.tenant_id).first()
    if not cliente: raise HTTPException(status_code=404, detail="Cliente no encontrado")

    update_data = cliente_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cliente, field, value)
    db.commit()
    db.refresh(cliente)
    return cliente

@router.delete("/{cliente_id}")
def delete_cliente(cliente_id: int, db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    cliente = db.query(models.cliente.Cliente).filter(models.cliente.Cliente.id == cliente_id, models.cliente.Cliente.tenant_id == current_user.tenant_id).first()
    if not cliente: raise HTTPException(status_code=404, detail="Cliente no encontrado")

    usuario = db.query(models.user.User).filter(models.user.User.id == cliente.user_id).first()
    db.delete(cliente)
    if usuario: db.delete(usuario)
    db.commit()
    return {"message": "Cliente eliminado exitosamente"}