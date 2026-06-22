import json
from confluent_kafka import Producer
from app.core.config import settings

class KafkaProducerClient:
    def __init__(self):
        conf = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': settings.PROJECT_NAME
        }
        self.producer = Producer(conf)

    def delivery_report(self, err, msg):
        if err is not None:
            print(f'Message delivery failed: {err}')

    def produce(self, topic, key, value):
        """Produce a JSON message to a Kafka topic."""
        self.producer.produce(
            topic, 
            key=str(key).encode('utf-8') if key else None, 
            value=json.dumps(value).encode('utf-8'), 
            callback=self.delivery_report
        )
        self.producer.poll(0)

    def flush(self):
        self.producer.flush()

producer = KafkaProducerClient()
