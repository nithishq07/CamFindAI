from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class UserBase(BaseModel):
    email: str
    role: str = "operator"

class UserOut(UserBase):
    id: int
    sso_provider: Optional[str] = None
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    orgName: str
    industry: str
    adminName: str
    email: str
    phone: str
    password: str
    orgSize: str

class CameraBase(BaseModel):
    name: str
    location: Optional[str] = None
    source_type: str = "RTSP"
    stream_url: str
    fps: int = 30

class CameraCreate(CameraBase):
    pass

class CameraOut(CameraBase):
    id: int
    is_recording: bool
    status: str
    last_seen: Optional[datetime] = None
    class Config:
        from_attributes = True

class ZoneBase(BaseModel):
    name: str
    camera_id: int
    coordinates: Any
    restricted: bool = False

class ZoneCreate(ZoneBase):
    pass

class ZoneOut(ZoneBase):
    id: int
    class Config:
        orm_mode = True

class PersonOut(BaseModel):
    global_id: str
    risk_score: float
    first_seen: datetime
    last_seen: datetime
    current_camera_id: Optional[int]
    class Config:
        orm_mode = True

class TrajectoryPointOut(BaseModel):
    id: int
    global_id: str
    camera_id: int
    zone_id: Optional[int]
    location_label: Optional[str]
    x: float
    y: float
    frame_ts: datetime
    class Config:
        orm_mode = True

class AlertOut(BaseModel):
    id: int
    severity: str
    alert_type: str
    frame_ts: datetime
    status: str
    camera_id: int
    zone_id: Optional[int]
    global_id: str
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    class Config:
        orm_mode = True

class AlertUpdate(BaseModel):
    status: str

class ReIDThresholdUpdate(BaseModel):
    threshold: float
