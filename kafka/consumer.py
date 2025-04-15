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
    """Validate and load data into the database

    Args:
        message (payload): data based on schema

    Returns:
        None
    """
    try:
        # Create cursor to interact with db
        cur = postgres_connection.cursor()

        # Validate if the game is already in db
        if game_validation(cur, message["game_id"]):
            logging.log(
                f"Inserting database into the database for game {message["game_id"]}"
            )
            insert_game(cur, message)

        """
        Validate team data
        If team not in db, insert new team
        """
        home = " ".join(message["game_data"]["home"].split(" ")[1:])
        away = " ".join(message["game_data"]["away"].split(" ")[1:])
        if team_validation(cur, home) == False:
            insert_team(cur, home)
        if team_validation(cur, away) == False:
            insert_team(cur, away)

        """
        Validate player data
        If player not in db, insert new player
        """
        for player in message["boxscore"]["home"]:
            if player_validation(cur) == False:
                insert_player(cur)

        for player in message["boxscore"]["away"]:
            if player_validation(cur) == False:
                insert_player(cur)
        """ 
        Validate game data and insert game specific data
        """

    except Exception as e:
        logging.error(f"Error with payload for game {message["game_id"]}")
    finally:
        cur.close()


def player_validation(cur) -> bool:
    return


def insert_player(cur) -> bool:
    return


def game_validation(cur, game_id) -> bool:
    cur.execute("SELECT id FROM game WHERE id = %s;", (game_id,))
    return cur.fetchone() is None


def team_validation(cur, mascot) -> bool:
    cur.execute("SELECT mascot FROM team WHERE id = %s;"(mascot))
    return cur.fetchone() is None


def insert_team(cur, team):
    pass


def insert_game(cur, message):
    pass


if __name__ == "__main__":
    logging.info("Consuming all messages")
    consume()
    load_data()
