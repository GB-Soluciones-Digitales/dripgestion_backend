from typing import Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import date
from app.models.user import UserRole
from app.schemas.logistica import MovimientoCreate, PagoManualCreate
from app.crud import crud_logistica
from app.models.cliente import Cliente
from app.models.producto import Producto

def registrar_entrega(db: Session, mov_in: MovimientoCreate, tenant_id: int):
    cliente = db.query(Cliente).filter(Cliente.id == mov_in.cliente_id, Cliente.tenant_id == tenant_id).first()
    if not cliente:
        raise ValueError("Cliente no encontrado")

    if not isinstance(cliente.stock_envases, dict):
        cliente.stock_envases = {}
    
    stock_actualizado = dict(cliente.stock_envases) 
    for producto_id, cant in mov_in.detalles.items():
        if str(producto_id) not in stock_actualizado:
            stock_actualizado[str(producto_id)] = 0
        entregado = cant.get('entregado', 0)
        devuelto = cant.get('devuelto', 0)
        stock_actualizado[str(producto_id)] += (entregado - devuelto)

    cliente.stock_envases = stock_actualizado
    
    deuda_generada = mov_in.monto_total - mov_in.monto_cobrado
    cliente.saldo_dinero += deuda_generada

    db.add(cliente)
           
    mov_data = {
        "tenant_id": tenant_id,
        "cliente_id": mov_in.cliente_id,
        "recorrido_id": mov_in.recorrido_id,
        "detalles": mov_in.detalles, 
        "monto_total": mov_in.monto_total,
        "monto_cobrado": mov_in.monto_cobrado,
        "metodo_pago": mov_in.metodo_pago,
        "observacion": mov_in.observacion
    }
    
    return crud_logistica.create_movimiento(db, mov_data)

def registrar_pago_manual(db: Session, cliente_id: int, pago_in: PagoManualCreate, tenant_id: int):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.tenant_id == tenant_id).first()
    if not cliente:
        raise ValueError("Cliente no encontrado")

    cliente.saldo_dinero -= pago_in.monto

    mov_data = {
        "tenant_id": tenant_id,
        "cliente_id": cliente_id,
        "recorrido_id": None, 
        "detalles": {}, 
        "monto_total": 0.0, 
        "monto_cobrado": pago_in.monto,
        "metodo_pago": pago_in.metodo_pago,
        "observacion": f"Pago de saldo. {pago_in.observacion}".strip()
    }
    crud_logistica.create_movimiento(db, mov_data)
    return {"message": "Pago registrado", "nuevo_saldo": cliente.saldo_dinero}

def obtener_historial_dia(db: Session, fecha: date, tenant_id: int):
    movimientos = crud_logistica.get_movimientos_dia(db, fecha, tenant_id)
    productos = db.query(Producto).filter(Producto.tenant_id == tenant_id).all()
    mapa_productos = {str(p.id): p.nombre for p in productos}
    
    resultados = []
    for mov, nombre_cliente in movimientos:
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

def obtener_resumen_mes(db: Session, user: Any):
    if user.role != UserRole.ADMIN:
        raise ValueError("No tienes permisos para ver el resumen mensual.")

    hoy = date.today()
    tenant_id = user.tenant_id
    
    movimientos = crud_logistica.get_movimientos_mes(db, hoy.month, hoy.year, tenant_id)

    efectivo = sum(m.monto_cobrado for m in movimientos if m.metodo_pago == 'efectivo')
    transferencia = sum(m.monto_cobrado for m in movimientos if m.metodo_pago == 'transferencia')

    deuda_en_calle = db.query(func.sum(Cliente.saldo_dinero))\
                        .filter(Cliente.tenant_id == tenant_id, Cliente.saldo_dinero > 0)\
                        .scalar() or 0.0
    
    return {
        "efectivo": efectivo, 
        "transferencia": transferencia, 
        "fiado": deuda_en_calle
    }