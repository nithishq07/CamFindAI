import json
from confluent_kafka import Consumer
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.schema import Person, TrajectoryPoint, Track
from datetime import datetime

def main():
    conf = {
        'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'persistence_group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe(['identity.matches'])
    
    print("Persistence Consumer started. Listening to 'identity.matches'...")

    db = SessionLocal()

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            data = json.loads(msg.value().decode('utf-8'))
            
            global_id = data["global_id"]
            camera_id = data["camera_id"]
            local_track_id = data["local_track_id"]
            frame_ts_str = data["frame_ts"]
            frame_ts = datetime.fromisoformat(frame_ts_str)
            x = data["x"]
            y = data["y"]

            # Upsert Person
            person = db.query(Person).filter(Person.global_id == global_id).first()
            if not person:
                person = Person(
                    global_id=global_id,
                    first_seen=frame_ts,
                    last_seen=frame_ts,
                    current_camera_id=camera_id
                )
                db.add(person)
            else:
                person.last_seen = frame_ts
                person.current_camera_id = camera_id
                
            # Upsert Track
            track = db.query(Track).filter(
                Track.local_track_id == local_track_id, 
                Track.camera_id == camera_id
            ).first()
            if not track:
                track = Track(
                    local_track_id=local_track_id,
                    camera_id=camera_id,
                    global_id=global_id,
                    start_ts=frame_ts
                )
                db.add(track)
            else:
                track.end_ts = frame_ts

            # Add Trajectory Point
            point = TrajectoryPoint(
                global_id=global_id,
                camera_id=camera_id,
                x=x,
                y=y,
                frame_ts=frame_ts
            )
            db.add(point)

            try:
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"DB Error: {e}")
                
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        db.close()

if __name__ == "__main__":
    main()
