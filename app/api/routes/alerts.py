from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schema import Alert
from app.schemas.pydantic_models import AlertOut, AlertUpdate
from app.api.routes.auth import get_current_user, RoleChecker
from datetime import datetime

router = APIRouter()

allow_operator = RoleChecker(["admin", "operator"])

@router.get("")
def list_alerts(
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    query = db.query(Alert).filter(Alert.org_id == current_user.org_id)
    if severity:
        query = query.filter(Alert.severity == severity)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
        
    total = query.count()
    items = query.order_by(Alert.frame_ts.desc()).offset(skip).limit(limit).all()
    return {"total": total, "skip": skip, "limit": limit, "items": items}

@router.patch("/{alert_id}", response_model=AlertOut)
def update_alert_status(
    alert_id: int, 
    data: AlertUpdate, 
    db: Session = Depends(get_db), 
    current_user = Depends(allow_operator)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    if data.status == "acknowledged":
        alert.status = "acknowledged"
        alert.acknowledged_by = current_user.id
        alert.acknowledged_at = datetime.utcnow()
    elif data.status == "resolved":
        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        if not alert.acknowledged_by: # Auto-ack if resolved directly
            alert.acknowledged_by = current_user.id
            alert.acknowledged_at = datetime.utcnow()
    else:
        alert.status = data.status
        
    db.commit()
    db.refresh(alert)
    return alert
