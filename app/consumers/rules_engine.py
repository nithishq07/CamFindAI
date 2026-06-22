import json
from confluent_kafka import Consumer, Producer
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.schema import Alert, Zone, Person
from datetime import datetime

def main():
    conf = {
        'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'rules_engine_group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe(['identity.matches'])
    
    prod_conf = {
        'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
        'client.id': settings.PROJECT_NAME
    }
    producer = Producer(prod_conf)
    
    print("Rules Engine Consumer started. Listening to 'identity.matches'...")

    db = SessionLocal()
    
    loitering_state = {}

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                continue

            data = json.loads(msg.value().decode('utf-8'))
            global_id = data["global_id"]
            camera_id = data["camera_id"]
            zone_id = data.get("zone_id")
            frame_ts = datetime.fromisoformat(data["frame_ts"])
            
            if zone_id:
                zone = db.query(Zone).filter(Zone.id == zone_id).first()
                if zone and zone.restricted:
                    alert_msg = {
                        "severity": "Critical",
                        "alert_type": "Restricted Area Access",
                        "frame_ts": data["frame_ts"],
                        "camera_id": camera_id,
                        "zone_id": zone_id,
                        "global_id": global_id
                    }
                    db_alert = Alert(
                        severity="Critical",
                        alert_type="Restricted Area Access",
                        frame_ts=frame_ts,
                        camera_id=camera_id,
                        zone_id=zone_id,
                        global_id=global_id
                    )
                    db.add(db_alert)
                    db.commit()
                    
                    producer.produce('alerts', key=str(camera_id).encode(), value=json.dumps(alert_msg).encode())
                    producer.poll(0)
            
            state_key = f"{global_id}_{camera_id}"
            if state_key not in loitering_state:
                loitering_state[state_key] = frame_ts
            else:
                elapsed = (frame_ts - loitering_state[state_key]).total_seconds()
                if elapsed > settings.LOITERING_THRESHOLD_SEC:
                    alert_msg = {
                        "severity": "Medium",
                        "alert_type": "Loitering Detection",
                        "frame_ts": data["frame_ts"],
                        "camera_id": camera_id,
                        "global_id": global_id
                    }
                    db_alert = Alert(
                        severity="Medium",
                        alert_type="Loitering Detection",
                        frame_ts=frame_ts,
                        camera_id=camera_id,
                        global_id=global_id
                    )
                    db.add(db_alert)
                    db.commit()
                    
                    producer.produce('alerts', key=str(camera_id).encode(), value=json.dumps(alert_msg).encode())
                    producer.poll(0)
                    
                    loitering_state[state_key] = frame_ts

            # --- DEFERRED ALERTS ---
            # The following alert types are recognized by the UI but are deferred for future implementation:
            # 
            # Simulated Rule 3: Abnormal Route
            # Requires historical trajectory clustering and deviation analysis.
            # 
            # Simulated Rule 4: Tailgating
            # Requires tracking multiple IDs moving through a restricted door zone concurrently.
            # 
            # Simulated Rule 5: Crowd Congestion
            # Requires counting unique track IDs in a single zone within a time window.
            # -----------------------

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        producer.flush()
        db.close()

if __name__ == "__main__":
    main()
