import sqlite3
import time

import click
from flask import current_app, g
import requests

from .models import Team, TeamPlayers

BASE_URL = "https://statsapi.mlb.com"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    # Fill teams
    rows_teams = getRowsOfTeams("/api/v1/standings?leagueId=103,104")
    db.executemany('INSERT INTO team (id, division_id, name, abbr, wins_this_season, losses_this_season, win_pct, wild_card_games_back, games_back, last_ten, run_diff, place_in_division) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', rows_teams)
    db.commit()

    rows_players = getRowsOfPlayers(rows_teams)
    db.executemany('INSERT INTO teamplayers (id, team_id) VALUES(?, ?);', rows_players)
    db.commit()

# Function generates a list of tuples to insert into table
def getRowsOfTeams(endpoint): 
    try:
        rows_teams = []
        response = requests.get(f"{BASE_URL}{endpoint}")
        response.raise_for_status()

        results = response.json()
        records = results['records']

        for div in records:
            t = Team.Team() 
            t.division_id = div['division']['id']
            for team in div['teamRecords']:
                # Insert appropriate values into object
                t.team_id = team['team']['id']
                t.name = team['team']['name']
                t.abbr = getTeamAbbr(team['team']['link'])
                t.wins_this_season = team['leagueRecord']['wins']
                t.losses_this_season = team['leagueRecord']['losses']
                t.win_pct = team['leagueRecord']['pct']
                t.wild_card_games_back = team['wildCardGamesBack']
                t.games_back = team['gamesBack']

                t.last_ten = str(team['records']['splitRecords'][8]['wins']) + "-" + str(team['records']['splitRecords'][8]['losses']) 

                t.run_diff = team['runDifferential']

                t.place_in_division = ordinal(team['divisionRank'])

                # Append as tuples
                rows_teams.append(t.as_tuple())

        return rows_teams
    except requests.exceptions.HTTPError as errh:
        e = Team.Team()
        return [e.as_tuple()]

def getRowsOfPlayers(teams_list):
    try:
        rows_players = []
        for team in teams_list:
           response = requests.get(f"{BASE_URL}/api/v1/teams/{team[0]}/roster")
           response.raise_for_status()

           results = response.json()
           roster = results['roster']

           for player in roster:
               tp = TeamPlayers.TeamPlayers()
               tp.player_id = player['person']['id']
               tp.team_id = player['parentTeamId']

               rows_players.append(tp.as_tuple())

           time.sleep(1)

        return rows_players
    except requests.exceptions.HTTPError as errh:
        e = TeamPlayers.TeamPlayers()
        return [e.as_tuple()]

def getTeamAbbr(endpoint):
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        response.raise_for_status()

        results = response.json()
        team = results['teams'][0]

        return team['abbreviation']
    except requests.exceptions.HTTPError as errh:
        print(errh)
        return "ZZZ"

def ordinal(num):
    if num == '1':
        return num + 'st'
    elif num == '2':
        return num + 'nd'
    elif num == '3':
        return num + 'rd'
    else:
        return num + 'th'


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
