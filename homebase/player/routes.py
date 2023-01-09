from flask import Blueprint, abort, render_template
import requests

from ..db import get_db

player_bp = Blueprint('player_bp', __name__)

@player_bp.route('/player/<player_id>')
def playerDetails(player_id):
    try:
        db = get_db()
        req = requests.get(f'https://statsapi.mlb.com/api/v1/people/{player_id}?hydrate=stats(group=[hitting,pitching,fielding],type=[yearByYear])')
        req.raise_for_status()

        results = req.json()

        player = results['people'][0]
        noStats = False

        # Get the player's current team
        getPlayerCurrentTeam(player, player_id, db)

        # Determine if this player has stats to display
        if "stats" in player:
            statDictList = []
            if player['primaryPosition']['name'] == "Pitcher":
                # Get pitching statistics
                statDict = getStatsByGroup(player['stats'], "pitching")
                statDictList.append(statDict)
                
            elif player['primaryPosition']['abbreviation'] == "TWP":
                # Get pitching and hitting statistics
                statDictPitching = getStatsByGroup(player['stats'], "pitching")
                statDictHitting = getStatsByGroup(player['stats'], "hitting")

                statDictList.append(statDictPitching)
                statDictList.append(statDictHitting)
            else:
                # Get hitting statistics
                statDict = getStatsByGroup(player['stats'], "hitting")
                statDictList.append(statDict)

            getAbbreviationsForTeams(statDictList, db)

            player['stats'] = statDictList

            return render_template('player/player_details.html', player=player, noStats=noStats)
        else:
            noStats = True
            return render_template('player/player_details.html', player=player, noStats=noStats)

    except requests.exceptions.HTTPError as errh:
        abort(errh.response.status_code)

def getPlayerCurrentTeam(playerDict, playerId, db):
    row = db.execute('SELECT team.id, team.name FROM team INNER JOIN teamplayers ON team.id = teamplayers.team_id WHERE teamplayers.id=?;', (playerId,)).fetchone()

    playerDict['currentTeam'] = row['name']
    playerDict['currentTeamId'] = row['id']

def getStatsByGroup(statsList, groupName):
    for s in statsList:
        if s['group']['displayName'] == groupName:
            return s

def getAbbreviationsForTeams(statDictList, db):
    for s in statDictList:
        for season in s['splits']:
            if "numTeams" not in season:
                row = db.execute('SELECT abbr FROM team WHERE id=?;', (season['team']['id'],)).fetchone()
                season['team']['abbr'] = row['abbr'] 
