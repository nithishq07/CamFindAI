from fastapi import APIRouter, Depends
from app.core.config import settings
from app.schemas.pydantic_models import ReIDThresholdUpdate
from app.api.routes.auth import get_current_user, RoleChecker
from pydantic import BaseModel

router = APIRouter()

allow_admin = RoleChecker(["admin"])

class AlertSettingsUpdate(BaseModel):
    loitering_threshold_sec: int

@router.get("/reid-threshold")
def get_reid_threshold(current_user = Depends(get_current_user)):
    return {"threshold": settings.REID_THRESHOLD}

@router.put("/reid-threshold")
def update_reid_threshold(data: ReIDThresholdUpdate, current_user = Depends(allow_admin)):
    settings.REID_THRESHOLD = data.threshold
    return {"threshold": settings.REID_THRESHOLD, "status": "updated"}

@router.get("/alert-rules")
def get_alert_rules(current_user = Depends(get_current_user)):
    return {"loitering_threshold_sec": settings.LOITERING_THRESHOLD_SEC}

@router.put("/alert-rules")
def update_alert_rules(data: AlertSettingsUpdate, current_user = Depends(allow_admin)):
    settings.LOITERING_THRESHOLD_SEC = data.loitering_threshold_sec
    return {"loitering_threshold_sec": settings.LOITERING_THRESHOLD_SEC, "status": "updated"}
