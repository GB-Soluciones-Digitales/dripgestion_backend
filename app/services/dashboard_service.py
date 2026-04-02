from typing import Any
from sqlalchemy.orm import Session
from datetime import date
from app.crud import crud_dashboard
from app.models.user import UserRole

def obtener_metricas_dashboard(db: Session, user: Any):
    tenant_id = user.tenant_id
    hoy = date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year
    
    total_clientes = crud_dashboard.count_clientes_activos(db, tenant_id)
    
    todos_los_clientes = crud_dashboard.get_all_clientes_for_envases(db, tenant_id)
    total_envases = sum(
        sum(c.stock_envases.values()) 
        for c in todos_los_clientes 
        if isinstance(c.stock_envases, dict)
    )

    saldos_pendientes = 0
    recaudacion_hoy = 0
    total_recaudado_mes = 0
    entregas_mes = 0
    grafico_metodos = []
    grafico_anual = []
    grafico_choferes = []

    if user.role == UserRole.ADMIN:
        saldos_pendientes = crud_dashboard.get_saldos_pendientes_totales(db, tenant_id)
        recaudacion_hoy = crud_dashboard.get_recaudacion_dia(db, hoy, tenant_id)
        
        movimientos_mes = crud_dashboard.get_movimientos_mes(db, tenant_id, mes_actual, anio_actual)
        total_recaudado_mes = sum(m.monto_cobrado for m in movimientos_mes)
        entregas_mes = len(movimientos_mes)
        
        pagos_efectivo = sum(m.monto_cobrado for m in movimientos_mes if getattr(m.metodo_pago, 'value', m.metodo_pago) == 'efectivo')
        pagos_transferencia = sum(m.monto_cobrado for m in movimientos_mes if getattr(m.metodo_pago, 'value', m.metodo_pago) == 'transferencia')
        pagos_fiado = sum(m.monto_total for m in movimientos_mes if getattr(m.metodo_pago, 'value', m.metodo_pago) == 'cta_corriente')

        grafico_metodos = [
            {"name": "Efectivo", "value": pagos_efectivo, "color": "#10b981"}, 
            {"name": "Transferencias", "value": pagos_transferencia, "color": "#25A7DA"}, 
            {"name": "A Cuenta", "value": pagos_fiado, "color": "#f97316"} 
        ]

        datos_anuales = crud_dashboard.get_recaudacion_anual(db, tenant_id, anio_actual)
        nombres_meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        grafico_anual = [{"name": mes, "total": 0} for mes in nombres_meses]
        
        for mes_num, total in datos_anuales:
            if mes_num:
                grafico_anual[int(mes_num)-1]["total"] = float(total)

        datos_choferes = crud_dashboard.get_rendimiento_choferes(db, tenant_id, mes_actual, anio_actual)
        grafico_choferes = [
            {"nombre": row.full_name or "Sin Nombre", "recaudado": float(row.recaudado), "entregas": row.entregas}
            for row in datos_choferes
        ]

    return {
        "kpis": {
            "clientes_activos": total_clientes,
            "total_envases": total_envases,
            "deuda_en_calle": float(saldos_pendientes),
            "recaudacion_hoy": float(recaudacion_hoy),
            "recaudacion_mes": float(total_recaudado_mes),
            "entregas_mes": entregas_mes
        },
        "grafico_metodos": grafico_metodos,
        "grafico_anual": grafico_anual,
        "grafico_choferes": grafico_choferes,
        "role": user.role
    }