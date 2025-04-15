from nba_api.live.nba.endpoints import BoxScore, boxscore
from nba_api.stats.endpoints import scoreboardv2

from typing import List, Dict
import isodate
from datetime import datetime
import logging


def available_games() -> List:
    """Retrieves list of game id's on the current day

    Returns:
        List: Current list of all games available
    """
    current_date = datetime.today().strftime("%Y-%m-%d")
    games_list = []
    scoreboard = scoreboardv2.ScoreboardV2(game_date=current_date)
    games = scoreboard.get_normalized_dict()["GameHeader"]
    for game in games:
        games_list.append(game["GAME_ID"])
    return games_list


def extract_activate_stats(stats_list):
    return [
        {
            "name": stat["name"],
            "jersey": stat["jerseyNum"],
            "points": stat["statistics"]["points"],
            "rebounds": stat["statistics"]["reboundsTotal"],
            "assists": stat["statistics"]["assists"],
            "steals": stat["statistics"]["steals"],
            "blocks": stat["statistics"]["blocks"],
            "minutes": round(
                isodate.parse_duration(stat["statistics"]["minutes"]).total_seconds()
                / 60
            ),
        }
        for stat in stats_list
        if stat["status"] == "ACTIVE" and stat["played"] == "1"
    ]


def get_game_player_data(id: str) -> tuple:
    """Retrieves both home and away player data for a given game

    Args:
        game_id (str): ID for the game data is pulled from

    Returns:
        tuple: contains home player data and away player data
    """
    live_boxscore = BoxScore(game_id=id)
    live_home_stats = live_boxscore.home_team_player_stats.data
    live_away_stats = live_boxscore.away_team_player_stats.data
    home_players = extract_activate_stats(live_home_stats)
    away_players = extract_activate_stats(live_away_stats)
    return (home_players, away_players)


def generate_scores_report() -> List:
    """Generates scores report for all games including player box scores

    Args:
        None

    Returns:
        List of the data
    """
    report = []
    game_ids = available_games()
    if len(game_ids) == 0:
        logging.info("No available games")
    for id in game_ids:
        game_data = {}
        # Extract boxscore data from players
        game_data["sport"] = "nba"
        player_data = get_game_player_data(id)
        game_data["game_id"] = id
        game_data["boxscore"] = {"home": player_data[0], "away": player_data[1]}

        # Extract Game data
        live_scores = get_scores_nba(id)
        game_data["Scores"] = live_scores
        report.append(game_data)
    return report


def get_scores_nba(id: str) -> Dict:
    """Generates quarter by quarter scoring for a given game

    Args:
        id (str): ID for the game data is pulled from
        
    Returns:
        Dictionary of the quarter data
    """
    game_data = boxscore.BoxScore(game_id=id).game.data

    home = game_data["homeTeam"]
    away = game_data["awayTeam"]

    data = {
        "Home Team": f"{home['teamCity']} {home['teamName']}",
        "Away Team": f"{away['teamCity']} {away['teamName']}",
        "Final Score": f"{home['score']} - {away['score']}",
        "Status": game_data["gameStatusText"],
    }

    # Add quarter breakdown
    for i, period in enumerate(home["periods"], 1):
        home_score = period["score"]
        away_score = away["periods"][i - 1]["score"]
        data[f"Q{i} Home"], data[f"Q{i} Away"] = home_score, away_score
    return data
