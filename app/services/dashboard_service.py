from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.models import cliente, logistica, user as user_model

def obtener_metricas_dashboard(db: Session, user: user_model.User):
    tenant_id = user.tenant_id
    hoy = date.today()
    
    total_clientes = db.query(cliente.Cliente).filter(cliente.Cliente.tenant_id == tenant_id).count()
    
    todos_los_clientes = db.query(cliente.Cliente).filter(cliente.Cliente.tenant_id == tenant_id).all()
    total_envases = sum(
        sum(c.stock_envases.values()) 
        for c in todos_los_clientes 
        if isinstance(c.stock_envases, dict)
    )

    if user.role == user_model.UserRole.ADMIN:
        saldos_pendientes = db.query(func.sum(cliente.Cliente.saldo_dinero)).filter(
            cliente.Cliente.tenant_id == tenant_id,
            cliente.Cliente.saldo_dinero > 0
        ).scalar() or 0
        
        recaudacion_hoy = db.query(func.sum(logistica.Movimiento.monto_cobrado)).filter(
            logistica.Movimiento.tenant_id == tenant_id,
            func.date(logistica.Movimiento.fecha) == hoy
        ).scalar() or 0
    else:
        saldos_pendientes = 0
        recaudacion_hoy = 0

    return {
        "clientes_activos": total_clientes,
        "total_envases": total_envases,
        "saldos_pendientes": saldos_pendientes,
        "recaudacion_hoy": recaudacion_hoy,
        "role": user.role
    }