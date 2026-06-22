from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schema import Camera
from app.schemas.pydantic_models import CameraOut, CameraCreate
from app.api.routes.auth import get_current_user, RoleChecker
from datetime import datetime, timedelta

router = APIRouter()

allow_admin = RoleChecker(["admin"])

@router.get("")
def list_cameras(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    total = db.query(Camera).filter(Camera.org_id == current_user.org_id).count()
    items = db.query(Camera).filter(Camera.org_id == current_user.org_id).offset(skip).limit(limit).all()
    return {"total": total, "skip": skip, "limit": limit, "items": items}

@router.post("", response_model=CameraOut)
def create_camera(camera: CameraCreate, db: Session = Depends(get_db), current_user = Depends(allow_admin)):
    db_cam = Camera(**camera.dict())
    db.add(db_cam)
    db.commit()
    db.refresh(db_cam)
    return db_cam

@router.put("/{camera_id}", response_model=CameraOut)
def update_camera(camera_id: int, camera: CameraCreate, db: Session = Depends(get_db), current_user = Depends(allow_admin)):
    db_cam = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    for key, value in camera.dict().items():
        setattr(db_cam, key, value)
        
    db.commit()
    db.refresh(db_cam)
    return db_cam

@router.delete("/{camera_id}")
def delete_camera(camera_id: int, db: Session = Depends(get_db), current_user = Depends(allow_admin)):
    db_cam = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    db.delete(db_cam)
    db.commit()
    return {"detail": "Camera deleted"}

@router.post("/{camera_id}/test")
def test_camera(camera_id: int, db: Session = Depends(get_db), current_user = Depends(allow_admin)):
    db_cam = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    from app.cameras.camera_manager import CameraSource
    cam_source = CameraSource(camera_id=db_cam.id, source_type=db_cam.source_type, stream_url=db_cam.stream_url)
    success = cam_source.connect()
    
    if success:
        fps = cam_source.get_fps()
        cam_source.disconnect()
        return {"status": "online", "fps": fps}
    else:
        return {"status": "offline", "fps": 0.0}

@router.post("/{camera_id}/start")
def start_camera(camera_id: int, db: Session = Depends(get_db), current_user = Depends(allow_admin)):
    db_cam = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    db_cam.status = "starting"
    db.commit()
    # In a real microservice arch, this might send a Kafka event to start the worker.
    # For now, the worker will pick it up on its next poll cycle.
    return {"detail": "Camera startup initiated"}

@router.post("/{camera_id}/stop")
def stop_camera(camera_id: int, db: Session = Depends(get_db), current_user = Depends(allow_admin)):
    db_cam = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    db_cam.status = "offline"
    db_cam.is_recording = False
    db.commit()
    return {"detail": "Camera shutdown initiated"}

@router.get("/{camera_id}/health-history")
def get_health_history(camera_id: int, range: str = "1h", db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    from app.models.schema import CameraHealthLog
    delta = timedelta(hours=1)
    if range == "24h":
        delta = timedelta(hours=24)
    elif range == "7d":
        delta = timedelta(days=7)
        
    cutoff = datetime.utcnow() - delta
    logs = db.query(CameraHealthLog).filter(
        CameraHealthLog.camera_id == camera_id,
        CameraHealthLog.timestamp >= cutoff
    ).order_by(CameraHealthLog.timestamp.asc()).all()
    
    return [
        {
            "timestamp": log.timestamp.isoformat(),
            "fps": log.fps,
            "status": log.status
        }
        for log in logs
    ]
