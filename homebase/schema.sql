DROP TABLE IF EXISTS division;
DROP TABLE IF EXISTS team;
DROP TABLE IF EXISTS teamplayers;


CREATE TABLE division (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    last_updated TEXT
);



CREATE TABLE team (
    id INTEGER PRIMARY KEY,
    division_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    abbr TEXT NOT NULL,
    wins_this_season INTEGER NOT NULL DEFAULT -1,
    losses_this_season INTEGER NOT NULL DEFAULT -1,
    win_pct TEXT NOT NULL DEFAULT '',
    wild_card_games_back TEXT NOT NULL DEFAULT '',
    games_back TEXT NOT NULL DEFAULT '',
    last_ten TEXT NOT NULL DEFAULT '',
    run_diff INTEGER NOT NULL DEFAULT -1,
    place_in_division TEXT,
    last_updated TEXT,
    FOREIGN KEY (division_id) REFERENCES division (id)
);

CREATE TABLE teamplayers (
    id INTEGER PRIMARY KEY,
    team_id INTEGER NOT NULL,
    FOREIGN KEY (team_id) REFERENCES team (id)
);


INSERT INTO division (id, name) VALUES (201, "AL East");
INSERT INTO division (id, name) VALUES (202, "AL Central");
INSERT INTO division (id, name) VALUES (200, "AL West");
INSERT INTO division (id, name) VALUES (204, "NL East");
INSERT INTO division (id, name) VALUES (205, "NL Central");
INSERT INTO division (id, name) VALUES (203, "NL West");

