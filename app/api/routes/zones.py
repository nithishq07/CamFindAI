from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schema import Zone
from app.schemas.pydantic_models import ZoneOut, ZoneCreate
from app.api.routes.auth import get_current_user, RoleChecker

router = APIRouter()

allow_admin = RoleChecker(["admin"])

@router.get("", response_model=List[ZoneOut])
def list_zones(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Zone).filter(Zone.org_id == current_user.org_id).all()

@router.post("", response_model=ZoneOut)
def create_zone(zone: ZoneCreate, db: Session = Depends(get_db), current_user = Depends(allow_admin)):
    db_zone = Zone(**zone.dict())
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone

@router.put("/{zone_id}", response_model=ZoneOut)
def update_zone(zone_id: int, zone: ZoneCreate, db: Session = Depends(get_db), current_user = Depends(allow_admin)):
    db_zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone not found")
        
    for key, value in zone.dict().items():
        setattr(db_zone, key, value)
        
    db.commit()
    db.refresh(db_zone)
    return db_zone
