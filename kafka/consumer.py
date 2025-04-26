from kafka import KafkaConsumer
import json
import logging
import psycopg2
from psycopg2.extensions import cursor
import os
from dotenv import load_dotenv
import redis
import datetime


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


        """
        Validate game data
        Game should not be a duplicate of another game
            -> If validation runs True, game does not exist hence we can insert
        """
        game_validation = validate_game(cur, message["game_id"])
        if game_validation:
            insert_game(cur, message["game_id"])


        """
        Validate team data
        If team not in db, insert new team
        """
        home_parts = message["game_data"]["home"].split(" ")
        away_parts = message["game_data"]["away"].split(" ")

        home_city = " ".join(home_parts[:-1])
        away_city = " ".join(home_parts[:-1])

        home_mascot = home_parts[-1]
        away_mascot = away_parts[-1]

        home_team_validation = validate_team(cur, home_mascot)
        away_team_validation = validate_team(cur, away_mascot)

        if not home_team_validation:
            insert_team(cur, home_city, home_mascot)
        if not away_team_validation:
            insert_team(cur, away_city, away_mascot)
          
            
        """
        Validate player data
        If player not in db, insert new player
        """
        home_players = message["boxscore"]["home"]
        away_players = message["boxscore"]["away"]
        for player in home_players:
            # logic
            pass
        for player in away_players:
            # logic
            pass
        """ 
        Validate game data and insert game specific data
        """

    except Exception as e:
        logging.error(f"Error with payload for game {message["game_id"]}")

    finally:
        cur.close()


def validate_game(cur: cursor, game_id: str) -> bool:
    """Validate that the game does not exists

    Args:
        cur (cursor): database connection
        game_id (str): id for the game being verified

    Returns:
        bool: True if the game does not exist, False otherwise
    """
    try:
        cur.execute("SELECT game_id FROM game WHERE id = %s;", (game_id,))
        result = cur.fetchone()
        if result is None:
            return True
        return False
    except Exception as e:
        logging.error(f"Unable to execute query for validating game {game_id}: {e}")
        return False


def insert_game(cur: cursor, game_id: str):
    try:
        date = datetime.today()
        cur.execute(
            "INSERT INTO game (id, game_date) VALUES (%s, %s);", (game_id, date)
        )
    except Exception as e:
        logging.error(f"Unable to execute query for inserting game {game_id}: {e}")


def validate_team(cur: cursor, mascot: str) -> bool:
    """Validate that the current team is within the database


    Args:
        cur (cursor): database connection
        mascot (str): mascot for the team

    Returns:
        bool: True if team is found, False otherwise
    """
    try:
        cur.execute("SELECT mascot FROM team WHERE mascot = %s;", (mascot,))
        result = cur.fetchone()
        if result is not None and len(result) == 1:
            return True
        return False
    except Exception as e:
        logging.error(f"Unable to execute query for validating team {mascot}: {e}")
        return False


def insert_team(cur: cursor, team_city: str, mascot: str):
    """Insert team into database

    Args:
        cur (cursor): database connection
        team_city (str): team city
        mascot (str): team name
    """
    try:
        cur.execute(
            "INSERT INTO team (city, mascot) VALUES (%s, %s);", (team_city, mascot)
        )
    except Exception as e:
        logging.error(
            f"Unable to execute query for inserting team {team_city} {mascot}: {e}"
        )


if __name__ == "__main__":
    logging.info("Consuming all messages")
    consume()
