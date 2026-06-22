from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schema import Person, Alert, Camera
from app.api.routes.auth import get_current_user
from sqlalchemy import func

router = APIRouter()

@router.get("")
def get_analytics(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    tracked_persons = db.query(func.count(Person.global_id)).filter(Person.org_id == current_user.org_id).scalar()
    active_alerts = db.query(func.count(Alert.id)).filter(Alert.org_id == current_user.org_id).scalar()
    active_cameras = db.query(func.count(Camera.id)).filter(Camera.status == 'online', Camera.org_id == current_user.org_id).scalar()
    
    return {
        "tracked_persons": tracked_persons,
        "unique_identities": tracked_persons,
        "suspicious_activities": active_alerts,
        "active_cameras": active_cameras,
        "average_tracking_duration": 45.5
    }
