from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import Base

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    size = Column(String, nullable=True)

    users = relationship("User", back_populates="organization")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True) # nullable for SSO
    role = Column(String, default="operator")
    sso_provider = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    organization = relationship("Organization", back_populates="users")

class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    source_type = Column(String, default="RTSP") # WEBCAM, IP_CAMERA, RTSP
    stream_url = Column(String, nullable=False)
    fps = Column(Integer, default=30)
    is_recording = Column(Boolean, default=False)
    status = Column(String, default="offline")
    last_seen = Column(DateTime(timezone=True), nullable=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    zones = relationship("Zone", back_populates="camera")
    tracks = relationship("Track", back_populates="camera")
    trajectory_points = relationship("TrajectoryPoint", back_populates="camera")
    alerts = relationship("Alert", back_populates="camera")
    health_logs = relationship("CameraHealthLog", back_populates="camera")

class Zone(Base):
    __tablename__ = "zones"
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    name = Column(String, nullable=False)
    coordinates = Column(JSON, nullable=False) # Polygon
    restricted = Column(Boolean, default=False)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    camera = relationship("Camera", back_populates="zones")

class Person(Base):
    __tablename__ = "persons"
    global_id = Column(String, primary_key=True, index=True) # e.g. "ID-0045"
    risk_score = Column(Float, default=0.0)
    first_seen = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    current_camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    tracks = relationship("Track", back_populates="person")
    trajectory_points = relationship("TrajectoryPoint", back_populates="person")
    alerts = relationship("Alert", back_populates="person")

class Track(Base):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True, index=True)
    local_track_id = Column(String, index=True, nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    global_id = Column(String, ForeignKey("persons.global_id"), nullable=False)
    start_ts = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    end_ts = Column(DateTime(timezone=True), nullable=True)

    camera = relationship("Camera", back_populates="tracks")
    person = relationship("Person", back_populates="tracks")

class TrajectoryPoint(Base):
    __tablename__ = "trajectory_points"
    id = Column(Integer, primary_key=True, index=True)
    global_id = Column(String, ForeignKey("persons.global_id"), nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    location_label = Column(String, nullable=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    frame_ts = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    camera = relationship("Camera", back_populates="trajectory_points")
    person = relationship("Person", back_populates="trajectory_points")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    severity = Column(String, nullable=False) # Critical, High, Medium, Low
    alert_type = Column(String, nullable=False)
    status = Column(String, default="open") # open, acknowledged, resolved
    frame_ts = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    global_id = Column(String, ForeignKey("persons.global_id"), nullable=False)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    camera = relationship("Camera", back_populates="alerts")
    person = relationship("Person", back_populates="alerts")
    acknowledger = relationship("User")

class CameraHealthLog(Base):
    __tablename__ = "camera_health_log"
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    fps = Column(Float, default=0.0)
    status = Column(String, nullable=False)

    camera = relationship("Camera", back_populates="health_logs")
