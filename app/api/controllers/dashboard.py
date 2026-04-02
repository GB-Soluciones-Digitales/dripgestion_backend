from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.services import dashboard_service

router = APIRouter()

@router.get("/resumen")
def get_dashboard_stats(db: Session = Depends(get_db), current_admin: User = Depends(deps.get_current_admin)):
    try:
        return dashboard_service.obtener_metricas_dashboard(db, current_admin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular métricas: {str(e)}")