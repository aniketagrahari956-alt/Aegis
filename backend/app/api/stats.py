from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict

from ..db.session import get_db
from ..db.models import Alert, IngestStats
from ..schemas.schemas import StatsOverview
from .auth import get_current_user, User

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/overview", response_model=StatsOverview)
def get_stats_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Total scanned from the rolling stats row
    stats_row = db.query(IngestStats).order_by(IngestStats.id.desc()).first()
    total_scanned = stats_row.total_scanned if stats_row else 0
    
    # Actual alerts in DB
    total_alerts = db.query(Alert).count()
    
    # Severity distribution
    severity_query = db.query(Alert.severity, func.count(Alert.id)).group_by(Alert.severity).all()
    severity_dist = {severity: count for severity, count in severity_query}
    # Ensure all severities are present
    for s in ["Critical", "High", "Medium", "Low"]:
        if s not in severity_dist:
            severity_dist[s] = 0
            
    # Label distribution
    label_query = db.query(Alert.predicted_label, func.count(Alert.id)).group_by(Alert.predicted_label).all()
    label_dist = {label: count for label, count in label_query}
    # Ensure expected keys are present (for consistent rendering)
    for l in ["dos", "probe", "r2l", "u2r", "suspicious"]:
        if l not in label_dist:
            label_dist[l] = 0
            
    # Fetch 10 most recent alerts
    recent_alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(10).all()
    
    return {
        "total_scanned": total_scanned,
        "total_alerts": total_alerts,
        "severity_distribution": severity_dist,
        "label_distribution": label_dist,
        "recent_alerts": recent_alerts
    }
