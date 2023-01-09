import sqlite3
import time
import datetime

import click
from flask import current_app, g
import requests

from .models import Division, Team, TeamPlayers

BASE_URL = "https://statsapi.mlb.com"

def get_db():
    '''
    Returns a connection object to the database, to be used throughout the application

    Parameters:
        none
    
    Returns:
        Return db object in the global context
    '''
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    '''
    Removes db object from the application context and closes the connection

    Parameters:
        none
    
    Returns:
        nothing
    '''
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    '''
    Initializes the database with a combination of a schema file and data from external mlb api

    Parameters:
        none

    Returns:
        nothing
    '''
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    # Fill teams
    rows_divisions, rows_teams = getRowsOfDivsTeams("/api/v1/standings?leagueId=103,104")
    db.executemany('UPDATE division SET last_updated=? WHERE id=?', rows_divisions)
    db.commit()
    db.executemany('INSERT INTO team (id, division_id, name, abbr, wins_this_season, losses_this_season, win_pct, wild_card_games_back, games_back, last_ten, run_diff, place_in_division, last_updated) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', rows_teams)
    db.commit()

    rows_players = getRowsOfPlayers(rows_teams)
    db.executemany('INSERT INTO teamplayers (id, team_id) VALUES(?, ?);', rows_players)
    db.commit()

# Function generates a list of tuples to insert into table
def getRowsOfDivsTeams(endpoint):
    '''
    Returns a tuple of lists of data to be entered in the division and team tables
    Data is from the mlb api

    Parameters:
        endpoint (str): A string containing the endpoint to the data needed

    Returns:
        rows_divisions (list of tuples), rows_teams (list of tuples)
    '''
    try:
        rows_divisions = []
        rows_teams = []
        response = requests.get(f"{BASE_URL}{endpoint}")
        response.raise_for_status()

        results = response.json()
        records = results['records']

        for div in records:
            d = Division.Division()
            d.division_id = div['division']['id']
            d.lastUpdated = div['lastUpdated']
            rows_divisions.append(d.as_tuple())

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

                t.lastUpdated = team['lastUpdated']

                # Append as tuples
                rows_teams.append(t.as_tuple())

        return rows_divisions, rows_teams
    except requests.exceptions.HTTPError as errh:
        e = Team.Team()
        return [e.as_tuple()]

def getRowsOfPlayers(teams_list):
    '''
    Returns a list of tuples of data to be entered into teamplayers table
    Iterates over each team's roster and collects player id and associated team id

    Parameters:
        teams_list (list): List of team ids
    
    Returns:
        rows_players (list): List of tuples to be entered in database
    '''
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
    '''
    Returns the abbreviations associated with team

    Parameters:
        endpoint (str): Endpoint to the data from the api
    
    Returns:
        The team abbreviation
        If there is an error with the request it will return ZZZ
    '''
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        response.raise_for_status()

        results = response.json()
        team = results['teams'][0]

        return team['abbreviation']
    except requests.exceptions.HTTPError as errh:
        return "ZZZ"

def ordinal(num):
    '''
    Converts number to its english (ordinal) representation

    Parameters:
        num (str): A str representing a number to be converted
    
    Returns:
        English representation of the passed number
    '''
    if num == '1':
        return num + 'st'
    elif num == '2':
        return num + 'nd'
    elif num == '3':
        return num + 'rd'
    else:
        return num + 'th'


def updateTeamRecords(record, db):
    '''
    Updates division and team tables if datestored in database is older than the one from api

    Parameters:
        record (dict): Dictionary containing the division information
        db (object): Reference to a database object connection
    
    Returns:
        Nothing
    '''
    # Compare datestrings
    # If database string is less than argument; update database
    db_datestring = db.execute('SELECT last_Updated FROM division WHERE id=?;', (record['division']['id'],)).fetchone()

    db_date = datetime.datetime.strptime(db_datestring['last_updated'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
    rec_date = datetime.datetime.strptime(record['lastUpdated'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
    
    if rec_date > db_date:
        recordsToUpdate = []
        for t in teamrecords:
            tr = Team.TeamRecords()
            tr.team_id = t['team']['id']
            tr.wins_this_season = t['leagueRecord']['wins']
            tr.losses_this_season = t['leagueRecord']['losses']
            tr.win_pct = t['leagueRecord']['pct']
            tr.wild_card_games_back = t['wildCardGamesBack']
            tr.games_back = t['gamesBack']
            tr.last_ten = str(t['records']['splitRecords'][8]['wins']) + "-" + str(t['records']['splitRecords'][8]['losses'])
            tr.run_diff = t['runDifferential']
            tr.place_in_division = ordinal(t['divisionRank'])
            tr.lastUpdated = t['lastUpdated']
            recordsToUpdate.append(tr.as_tuple())
        
        # Update teams table
        db.executemany('UPDATE team SET wins_this_season=?, losses_this_season=?, win_pct=?, wild_card_games_back=?, games_back=?, last_ten=?, run_diff=?, place_in_division=?, last_updated=? WHERE id=?;', recordsToUpdate)
        db.commit()

        # Update division table
        db.execute('UPDATE division SET last_updated=? WHERE id=?', (record['lastUpdated'], record['division']['id']))
        db.commit()




@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    '''
    On app initialization, add the initialize database command
    '''
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
