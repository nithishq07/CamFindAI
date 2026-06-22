from app.core.database import SessionLocal
from app.models.schema import Camera

def main():
    db = SessionLocal()
    
    cam1 = db.query(Camera).filter(Camera.id == 1).first()
    if not cam1:
        cam1 = Camera(id=1)
        db.add(cam1)
        
    cam1.name = "Realme"
    cam1.location = "Zone 1"
    cam1.source_type = "WEBCAM"
    cam1.stream_url = "0"
    cam1.status = "starting"
    cam1.is_recording = True
    
    cam2 = db.query(Camera).filter(Camera.id == 2).first()
    if not cam2:
        cam2 = Camera(id=2)
        db.add(cam2)
        
    cam2.name = "iPhone (Iriun)"
    cam2.location = "Zone 2"
    cam2.source_type = "WEBCAM"
    cam2.stream_url = "1"
    cam2.status = "starting"
    cam2.is_recording = True

    cam3 = db.query(Camera).filter(Camera.id == 3).first()
    if not cam3:
        cam3 = Camera(id=3)
        db.add(cam3)
        
    cam3.name = "MacBook Webcam"
    cam3.location = "Zone 3"
    cam3.source_type = "WEBCAM"
    cam3.stream_url = "2"
    cam3.status = "starting"
    cam3.is_recording = True
    
    db.commit()
    db.close()
    
    print("Successfully added Camera 1 (Realme), Camera 2 (iPhone), and Camera 3 (MacBook).")

if __name__ == "__main__":
    main()
