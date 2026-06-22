from app.core.database import SessionLocal
from app.models.schema import Camera, Zone

def seed():
    db = SessionLocal()
    
    # Create test cameras
    cam1 = db.query(Camera).filter(Camera.id == 1).first()
    if not cam1:
        cam1 = Camera(
            id=1,
            name="Main Entrance",
            location="Lobby",
            rtsp_url="test_video_1.mp4",
            fps=30,
            status="online"
        )
        db.add(cam1)

    cam2 = db.query(Camera).filter(Camera.id == 2).first()
    if not cam2:
        cam2 = Camera(
            id=2,
            name="Corridor B",
            location="Floor 2",
            rtsp_url="test_video_2.mp4",
            fps=30,
            status="online"
        )
        db.add(cam2)
        
    db.commit()

    # Create a test zone for Main Entrance
    if not db.query(Zone).filter(Zone.camera_id == 1).first():
        zone1 = Zone(
            camera_id=1,
            name="Lobby Restricted Area",
            coordinates={"points": [{"x": 100, "y": 100}, {"x": 500, "y": 100}, {"x": 500, "y": 500}, {"x": 100, "y": 500}]},
            restricted=True
        )
        db.add(zone1)
        
    db.commit()
    db.close()
    print("Database seeded successfully with test cameras and zones.")

if __name__ == "__main__":
    seed()
