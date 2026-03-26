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
    if not recorrido:
        raise HTTPException(status_code=404, detail="Recorrido no encontrado")

    if current_user.role == models.user.UserRole.REPARTIDOR:
        if recorrido.repartidor_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tenés permiso para ver este recorrido")
 
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

@router.patch("/recorridos/{recorrido_id}/asignar-repartidor", response_model=schemas.RecorridoResponse)
def asignar_repartidor(recorrido_id: int, body: RecorridoAsignarRepartidor, db: Session = Depends(get_db), current_admin: models.user.User = Depends(deps.get_current_admin)):
    recorrido = crud_logistica.get_recorrido(db, recorrido_id, current_admin.tenant_id)
    if not recorrido:
        raise HTTPException(status_code=404, detail="Recorrido no encontrado")
 
    try:
        return crud_logistica.update_recorrido_repartidor(
            db, recorrido, body.repartidor_id, current_admin.tenant_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/recorridos/{recorrido_id}")
def delete_recorrido(recorrido_id: int, db: Session = Depends(get_db), current_admin: models.user.User = Depends(deps.get_current_admin)):
    recorrido = crud_logistica.get_recorrido(db, recorrido_id, current_admin.tenant_id)
    if not recorrido:
        raise HTTPException(status_code=404, detail="Recorrido no encontrado")
    crud_logistica.delete_recorrido(db, recorrido)
    return {"message": "Recorrido eliminado exitosamente"}

@router.post("/movimientos")
def registrar_movimiento(mov_in: schemas.MovimientoCreate, db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    if current_user.role == models.user.UserRole.CLIENTE:
        raise HTTPException(status_code=403, detail="Los clientes no pueden registrar movimientos")
    try:
        return logistica_service.registrar_entrega(db, mov_in, current_user, current_user.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/movimientos/pago/{cliente_id}")
def registrar_pago_manual(cliente_id: int, pago_in: PagoManualCreate, db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    if current_user.role == models.user.UserRole.CLIENTE:
        raise HTTPException(status_code=403, detail="Los clientes no pueden registrar pagos")
    try:
        return logistica_service.registrar_pago_manual(db, cliente_id, pago_in, current_user, current_user.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/historial")
def get_historial_por_fecha(fecha: Optional[date] = None, db: Session = Depends(get_db), current_user: models.user.User = Depends(deps.get_current_user)):
    if current_user.role == models.user.UserRole.CLIENTE:
        raise HTTPException(status_code=403, detail="Acceso no permitido")
 
    if not fecha:
        fecha = date.today()
 
    if current_user.role == models.user.UserRole.REPARTIDOR:
        movimientos_raw = crud_logistica.get_movimientos_by_repartidor(
            db, current_user.id, current_user.tenant_id, fecha
        )
        from app.models.producto import Producto
        productos = db.query(Producto).filter(Producto.tenant_id == current_user.tenant_id).all()
        mapa_productos = {str(p.id): p.nombre for p in productos}
        resultados = []
        for mov, nombre_cliente in movimientos_raw:
            detalles_texto = []
            if mov.detalles:
                for prod_id, cant in mov.detalles.items():
                    entregados = cant.get("entregado", 0)
                    if entregados > 0:
                        nombre_prod = mapa_productos.get(str(prod_id), "Producto")
                        detalles_texto.append(f"{entregados} {nombre_prod}")
            texto_productos = " + ".join(detalles_texto) if detalles_texto else "Solo cobro / Sin entrega"
            resultados.append({
                "id": mov.id,
                "hora": mov.fecha.strftime("%H:%M"),
                "cliente": nombre_cliente,
                "metodo_pago": mov.metodo_pago,
                "monto_total": mov.monto_total,
                "monto_cobrado": mov.monto_cobrado,
                "resumen_productos": texto_productos,
                "observacion": mov.observacion
            })
        return resultados
 
    return logistica_service.obtener_historial_dia(db, fecha, current_user.tenant_id)
 
@router.get("/historial/mes-actual")
def get_resumen_mes_actual(db: Session = Depends(get_db), current_admin: models.user.User = Depends(deps.get_current_admin)):
    try:
        return logistica_service.obtener_resumen_mes(db, current_admin)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))