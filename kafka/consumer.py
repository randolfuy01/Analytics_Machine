from kafka import KafkaConsumer
import json
import logging
import psycopg2
import os
from dotenv import load_dotenv
import redis

load_dotenv()
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

redis_cache = redis.Redis(
    host="localhost:9091",
    decode_responses=True,
)

validation_queries = [
    "SELECT game.id FROM game WHERE game.id = %s;",
    "SELECT team.tname FROM team WHERE team.tname = %s;",
    "SELECT player.pname FROM player WHERE player.pname = %s;",
]


def consume():
    """Consume the kafka messages, cache the events within redis until the event is finished."""
    for message in consumer:
        try:
            if message["game_status"] != 3:
                # As long as the event is not processed, update key value pairs live
                redis_cache.set(message["game_id"], message)
            else:
                # After finished processing, load the data into the database and delete the key val
                load_data(message)
                redis_cache.delete(message["game_id"])
        except Exception as e:
            logging.error(f"Error processing message: {e}")


def load_data(message):
    try:
        with postgres_connection.cursor() as curs:
            # If game already exists, alert the system
            if game_validation(message):
                logging.log(f"Game {message["game_id"]} already exists")
            validate_players = True
            for player in message["boxscore"]["home"]:
                validate_players = validate_players and player_validation(
                    player["name"], message[""]
                )
    except Exception as e:
        logging.log(f"Error loading data into database: {e}")


def game_validation(message) -> bool:
    """Game Validation, check if game id already exists

    Args:
        message (None): payload

    Returns:
        bool: return false if the game is logged
    """
    cur = postgres_connection.cursor()
    cur.execute(validation_queries[0], message["game_id"])
    result = cur.fetchone()
    game_validation = result is not None
    cur.close()
    return not game_validation


def player_validation(player, team: str) -> bool:
    """Player Validation, check if player already exists with team and name

    Args:
        team (None): player payload
        team (Str): team player plays for
    Returns:
        bool: return false if the player already exists
    """
    cur = postgres_connection.cursor()
    cur.execute(validation_queries[2], player["player_name"], player["pname"])
    cur.execute(
        """
                SEELCT COUNT(*)
                FROM player
                JOIN team ON player.team_id = %s
                WHERE team_tname = %s AND player.pname = %s
                """,
        player["name"],
        team,
    )
    result = cur.fetchone()
    player_validation = result is not None
    return not player_validation


if __name__ == "__main__":
    logging.info("Consuming all messages")
    consume()
    load_data()
