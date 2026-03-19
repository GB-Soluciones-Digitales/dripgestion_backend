from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app import schemas, models
from app.api import deps
from app.db.session import get_db
from app.schemas.logistica import PagoManualCreate
from app.services import logistica_service
from app.crud import crud_logistica

router = APIRouter()

@router.post("/recorridos", response_model=schemas.RecorridoResponse)
def create_recorrido(recorrido_in: schemas.RecorridoCreate, db: Session = Depends(get_db), current_admin: models.user.User = Depends(deps.get_current_admin)):
    return crud_logistica.create_recorrido(db, recorrido_in.model_dump(), current_admin.tenant_id)

@router.get("/recorridos", response_model=List[schemas.RecorridoResponse])
def get_recorridos(db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    return crud_logistica.get_recorridos_smart(db, current_user)

@router.get("/recorridos/{recorrido_id}", response_model=schemas.RecorridoResponse)
def get_recorrido_by_id(recorrido_id: int, db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    recorrido = crud_logistica.get_recorrido(db, recorrido_id, current_user.tenant_id)
    if not recorrido: raise HTTPException(status_code=404, detail="Recorrido no encontrado")
    return recorrido

@router.put("/recorridos/{recorrido_id}", response_model=schemas.RecorridoResponse)
def update_recorrido(recorrido_id: int, recorrido_in: schemas.RecorridoUpdate, db: Session = Depends(get_db), current_admin: models.user.User = Depends(deps.get_current_admin)):
    recorrido = crud_logistica.get_recorrido(db, recorrido_id, current_admin.tenant_id)
    
    if not recorrido: 
        raise HTTPException(status_code=404, detail="Recorrido no encontrado")
        
    if recorrido_in.nombre: 
        recorrido.nombre = recorrido_in.nombre
    if recorrido_in.clientes_orden is not None: 
        recorrido.clientes_orden = recorrido_in.clientes_orden
        
    db.commit()
    db.refresh(recorrido)
    return recorrido

@router.delete("/recorridos/{recorrido_id}")
def delete_recorrido(recorrido_id: int, db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    recorrido = crud_logistica.get_recorrido(db, recorrido_id, current_user.tenant_id)
    if not recorrido: raise HTTPException(status_code=404, detail="Recorrido no encontrado")
    crud_logistica.delete_recorrido(db, recorrido)
    return {"message": "Recorrido eliminado exitosamente"}

@router.post("/movimientos")
def registrar_movimiento(mov_in: schemas.MovimientoCreate, db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    try:
        return logistica_service.registrar_entrega(db, mov_in, current_user.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/movimientos/pago/{cliente_id}")
def registrar_pago_manual(cliente_id: int, pago_in: PagoManualCreate, db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    try:
        return logistica_service.registrar_pago_manual(db, cliente_id, pago_in, current_user.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/historial")
def get_historial_por_fecha(fecha: Optional[date] = None, db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    if not fecha: fecha = date.today()
    return logistica_service.obtener_historial_dia(db, fecha, current_user.tenant_id)

@router.get("/historial/mes-actual")
def get_resumen_mes_actual(db: Session = Depends(get_db), current_admin: models.user.User = Depends(deps.get_current_admin)):
    return logistica_service.obtener_resumen_mes(db, current_admin.tenant_id)