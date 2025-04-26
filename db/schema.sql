-- Schema / Table Creation

-- Connect to different database
\c postgres;

-- Drop current database
DROP DATABASE IF EXISTS analytics;

-- Create database
CREATE DATABASE analytics;

-- Connect to database
\c analytics;

-- Create 'Game' Table
CREATE TABLE game (
    id VARCHAR(30) NOT NULL PRIMARY KEY,
    game_date DATE,
);

-- Create 'Team' Table
CREATE TABLE team (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255),
    mascot VARCHAR(255)
);

-- Create 'Score' Table
CREATE TABLE score (
    id SERIAL PRIMARY KEY,
    game_id INT NOT NULL,
    team_id INT NOT NULL,
    game_period INT,
    period_score INT,
    FOREIGN KEY (game_id) REFERENCES game(id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES team(id) ON DELETE CASCADE
);

-- Create enumeration for the player position
CREATE TYPE player_position AS ENUM ('PG', 'SG', 'SF', 'PF', 'C');

-- Create 'Player' Table
CREATE TABLE player (
    id SERIAL PRIMARY KEY, 
    team_id INT NOT NULL,
    pname VARCHAR(255),
    position player_position,
    jersey INT,
    FOREIGN KEY (team_id) REFERENCES team(id) ON DELETE CASCADE,
    CONSTRAINT unique_team_player UNIQUE (team_id, pname)
);


-- Create 'Stat' Table
CREATE TABLE stat (
    id INT SERIAL PRIMARY KEY,
    player_id INT NOT NULL,
    game_id INT NOT NULL,
    points INT,
    rebounds INT,
    assists INT,
    blocks INT,
    steals INT,
    minutes_played INT,
    FOREIGN KEY (player_id) REFERENCES player(id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES game(id) ON DELETE CASCADE
);
