-- Insertion execution queries

-- Insert a game into the database
INSERT INTO Game (id, game_date, game_location)
VALUES (%s, %s, %s);

-- Insert a team into the database
INSERT INTO Team (id, city, tname)
VALUES (%s, %s, %s);

-- Insert a player into the database
INSERT INTO player (id, team_id, pname, position, jersey)
VALUES (%s, %s, %s, %s, %s);
