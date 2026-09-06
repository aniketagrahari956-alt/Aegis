from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from ..db.session import get_db
from ..db.models import Alert
from ..schemas.schemas import AlertResponse, AlertUpdate
from .auth import get_current_user, User

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("", response_model=List[AlertResponse])
def list_alerts(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity_filter: Optional[str] = Query(None, alias="severity"),
    label_filter: Optional[str] = Query(None, alias="label"),
    source_filter: Optional[str] = Query(None, alias="source"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    
    if status_filter:
        query = query.filter(Alert.status == status_filter)
    if severity_filter:
        query = query.filter(Alert.severity == severity_filter)
    if label_filter:
        query = query.filter(Alert.predicted_label == label_filter)
    if source_filter:
        query = query.filter(Alert.source_identifier.ilike(f"%{source_filter}%"))
        
    # Order by newest first
    alerts = query.order_by(Alert.timestamp.desc()).offset(offset).limit(limit).all()
    return alerts

@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    payload: AlertUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found."
        )
        
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(alert, key, value)
        
    db.commit()
    db.refresh(alert)
    return alert
