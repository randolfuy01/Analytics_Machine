from kafka import KafkaConsumer
import json
import logging
import psycopg2
import os
from dotenv import load_dotenv

POSTGRES_USER = os.getenv("Postgres_user")
POSTGRES_PASS = os.getenv("Postgres_password")

consumer = KafkaConsumer(
    "nba-scores",
    bootstrap_servers="localhost:9092",
    group_id="nba-group",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

postgres_connection = psycopg2.connect(
    database="sports_analytics",
    user=POSTGRES_USER,
    password=POSTGRES_PASS,
    host="localhost",
    port=5432,
)


def consume():
    for message in consumer:
        try:
            game_data = message.value
        except Exception as e:
            logging.error(f"Error processing message: {e}")


def load_data():
    pass
