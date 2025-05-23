import json
from kafka import KafkaProducer
from api.nba import generate_scores_report
from jsonschema import validate, ValidationError
import logging

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)
    
    
def send_kafka_data():
    """Validating and sending data to Kafka via producer"""
    nba_data = generate_scores_report()
    if len(nba_data) != 0 and isinstance(nba_data, list):
        for game in nba_data:
            try:
                producer.send("nba-scores", game)
            except ValidationError as e:
                logging.warning(f"Skipping bad record: {e.message}")


if __name__ == "__main__":
    send_kafka_data()
