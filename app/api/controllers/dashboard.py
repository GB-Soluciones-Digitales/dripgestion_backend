from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models import user
from app.services import dashboard_service

router = APIRouter()

@router.get("/resumen")
def get_dashboard_stats(db: Session = Depends(get_db), current_admin: user.User = Depends(get_current_admin)
):
    return dashboard_service.obtener_metricas_dashboard(db, current_admin.tenant_id)