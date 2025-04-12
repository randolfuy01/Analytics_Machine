-- Schema / Table Creation

-- Connect to different database
\c postgres;

-- Drop current database
DROP DATABASE IF EXISTS Analytics;

-- Create database
CREATE DATABASE Analytics;

-- Connect to database
\c Analytics;

-- Create 'Game' Table
CREATE TABLE Game (
    ID int NOT NULL PRIMARY KEY,
    game_date date,
    game_location int
);

-- Create 'Team' Table
CREATE TABLE Team (
    ID int SERIAL PRIMARY KEY,
    City varchar(255),
    Team_name varchar(255)
);

-- Create 'Score' Table
CREATE TABLE Score (
    ID SERIAL PRIMARY KEY,
    Game_ID int NOT NULL,
    Team_ID int NOT NULL,
    Game_Period int,
    Period_score int,
    FOREIGN KEY (Game_ID) REFERENCES Game(ID) ON DELETE CASCADE,
    FOREIGN KEY (Team_ID) REFERENCES Team(ID) ON DELETE CASCADE
);

-- Create enumeration for the player position
CREATE TYPE player_position AS ENUM ('PG', 'SG', 'SF', 'PF', 'C');

-- Create 'Player' Table
CREATE TABLE Player (
    ID int SERIAL PRIMARY KEY,
    Team_ID int NOT NULL,
    Position player_position,
    Jersey int,
    FOREIGN KEY (Team_ID) REFERENCES Team(ID) ON DELETE CASCADE
);

-- Create 'Stat' Table
CREATE TABLE Stat (
    ID int SERIAL PRIMARY KEY,
    Player_ID int NOT NULL,
    Game_ID int NOT NULL,
    Points int,
    Rebounds int,
    Assists int,
    Blocks int,
    Minutes_played int,
    FOREIGN KEY (Player_ID) REFERENCES Player(ID) ON DELETE CASCADE,
    FOREIGN KEY (Game_ID) REFERENCES Game(ID) ON DELETE CASCADE
);