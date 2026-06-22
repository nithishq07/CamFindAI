import json
import numpy as np
import time
import collections
import sqlalchemy.exc
from confluent_kafka import Consumer, Producer
from app.core.config import settings
from app.pipeline.matcher import IdentityMatcher

def main():
    conf = {
        'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'matching_engine_group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe(['reid.embeddings'])
    
    prod_conf = {
        'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
        'client.id': settings.PROJECT_NAME
    }
    producer = Producer(prod_conf)
    
    matcher = IdentityMatcher(threshold=settings.REID_THRESHOLD)

    print("Matching Engine Consumer started. Listening to 'reid.embeddings'...")

    faiss_times = collections.deque(maxlen=100)
    kafka_times = collections.deque(maxlen=100)
    msg_counter = 0

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            data = json.loads(msg.value().decode('utf-8'))
            
            embedding_list = data.get("embedding")
            if not embedding_list:
                continue
                
            embedding = np.array(embedding_list, dtype=np.float32)
            
            max_retries = 5
            retry_delay = 1.0
            
            for attempt in range(max_retries):
                try:
                    t_faiss_start = time.perf_counter()
                    global_id = matcher.match(embedding, camera_id=data["camera_id"], frame_ts_str=data["frame_ts"])
                    t_faiss_end = time.perf_counter()
                    faiss_times.append(t_faiss_end - t_faiss_start)
                    
                    # Produce to identity.matches
                    t_kafka_start = time.perf_counter()
                    match_msg = {
                        "camera_id": data["camera_id"],
                        "local_track_id": data["local_track_id"],
                        "global_id": global_id,
                        "x": data["x"],
                        "y": data["y"],
                        "frame_ts": data["frame_ts"]
                    }
                    producer.produce(
                        'identity.matches',
                        key=str(data["camera_id"]).encode('utf-8'),
                        value=json.dumps(match_msg).encode('utf-8')
                    )
                    producer.poll(0)
                    t_kafka_end = time.perf_counter()
                    kafka_times.append(t_kafka_end - t_kafka_start)
                    break # Success
                except sqlalchemy.exc.OperationalError as e:
                    if attempt == max_retries - 1:
                        print(f"Max retries reached for OperationalError. Crashing consumer.")
                        raise
                    print(f"DB OperationalError: {e}. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
            
            msg_counter += 1
            if msg_counter % 100 == 0:
                avg_faiss = sum(faiss_times) / len(faiss_times) * 1000 if faiss_times else 0
                avg_kafka = sum(kafka_times) / len(kafka_times) * 1000 if kafka_times else 0
                print(f"[MATCHING ENGINE PROFILING] Avg Times over 100 queries - FAISS: {avg_faiss:.2f}ms | Kafka: {avg_kafka:.2f}ms")
            
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        producer.flush()

if __name__ == "__main__":
    main()
