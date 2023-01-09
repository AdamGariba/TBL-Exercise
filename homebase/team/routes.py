import copy
from flask import Blueprint, abort, render_template
import requests

from ..db import get_db

team_bp = Blueprint('team_bp', __name__)

@team_bp.route('/team/<team_id>')
def teamDetails(team_id):
    '''
    Gets information related to a roster of a team and renders the team page view with data

    Parameters:
        team_id (int): The id of the team being fetched
    
    Returns:
        Redirects to the team view with the necessary data
    '''
    try:
        # Get team info
        db = get_db()
        teamInfo = db.execute("SELECT team.id, team.name, division.name AS division_name, team.wins_this_season, team.losses_this_season, team.win_pct, team.games_back, team.place_in_division FROM team INNER JOIN division ON team.division_id=division.id WHERE team.id=?", (team_id,)).fetchone()


        req = requests.get(f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster/Active?hydrate=person(stats(type=season))")
        req.raise_for_status()

        results = req.json()
        roster = results['roster']

        # Split the hitters and pitchers into two lists of dictionaries
        pitchers = []
        hitters = []

        for player in roster:
            if player['position']['abbreviation'] == "P":
                player = calculatePitchingStats(player['person'], 0)

                pitchers.append(player)
            elif player['position']['abbreviation'] == "TWP":
                # Need to get pitcher and hitter stats seperately for this type of player
                print("For shohei ohtani")
                twoWayPlayer, pitchIdx, hitIdx = getTwoWayPlayerStats(player['person']['id'])

                hitter = copy.deepcopy(player)
                pitcher = copy.deepcopy(player) 

                pitcher['person']['stats'][0] = twoWayPlayer['stats'][pitchIdx]
                pitchers.append(pitcher['person'])

                hitter['person']['stats'][0] = twoWayPlayer['stats'][hitIdx]
                hitters.append(hitter['person'])

            else:
                player = calculateHittingStats(player['person'], 0)

                hitters.append(player)


        return render_template('team/team_details.html', teamInfo=teamInfo, pitchers=pitchers, hitters=hitters)
    except requests.exceptions.HTTPError as errh:
        abort(errh.response.status_code)


def calculatePitchingStats(pitcher, statIndex):
    '''
    Returns a dictionary referring to a pitcher's stats with the calculated stats included

    Parameters:
        pitcher (dict): A dictionary for a specific pitcher
        statIndex (int): A number indicated the index that the pitching stats are located
    
    Returns:
        Dictionary with the calculated stats included
    '''
    if "stats" in pitcher:
        bf = pitcher['stats'][statIndex]['splits'][0]['stat']['battersFaced'] 
        so = pitcher['stats'][statIndex]['splits'][0]['stat']['strikeOuts'] 
        bb = pitcher['stats'][statIndex]['splits'][0]['stat']['baseOnBalls'] 

        # only if batters faced is not 0
        if bf > 0:
            pitcher['stats'][statIndex]['splits'][0]['stat']['soPercent'] = int(round((so / bf) * 100, 0))
            pitcher['stats'][statIndex]['splits'][0]['stat']['bbPercent'] = int(round((bb / bf) * 100, 0))

    return pitcher

def calculateHittingStats(hitter, statIndex):
    '''
    Returns a dictionary referring to a hitter's stats with the calculated stats included

    Parameters:
        hitter (dict): A dictionary for a specific hitter
        statIndex (int): A number indicated the index that the pitching stats are located
    
    Returns:
        Dictionary with the calculated stats included
    '''
    if "stats" in hitter:
        pa = hitter['stats'][statIndex]['splits'][0]['stat']['plateAppearances'] 
        so = hitter['stats'][statIndex]['splits'][0]['stat']['strikeOuts'] 
        bb = hitter['stats'][statIndex]['splits'][0]['stat']['baseOnBalls'] 

        # only if plate appearances is not 0
        if pa > 0:
            hitter['stats'][statIndex]['splits'][0]['stat']['soPercent'] = round((so / pa) * 100, 1)
            hitter['stats'][statIndex]['splits'][0]['stat']['bbPercent'] = round((bb / pa) * 100, 1)

    return hitter

def getTwoWayPlayerStats(playerId):
    '''
    Returns a dictionary with the calculated stats for a two-way player (significant pitching and hitting stats)

    Parameters:
        playerId (int): Id for the player
    
    Returns:
        twoWayPlayer (dict): Dictionary containing the player's calculated stats
        pitchIdx (int): Number indicating where the player's pitching stats are located in dictionary
        hitIdx (int): Number indicating where the player's hitting stats are located in the dictionary
    '''
    try:
        tw_req = requests.get(f"https://statsapi.mlb.com/api/v1/people/{playerId}?hydrate=stats(group=[hitting,pitching],type=[season])")
        tw_req.raise_for_status()
        
        result = tw_req.json()

        twoWayPlayer = result['people'][0]

        pitchIdx = 0
        hitIdx = 0

        # Need to check ordering of list since api returns the order of pitching and hitting differently
        if twoWayPlayer['stats'][0]['group']['displayName'] == "pitching":
            twoWayPlayer = calculatePitchingStats(twoWayPlayer, 0)
            twoWayPlayer = calculateHittingStats(twoWayPlayer, 1)
            pitchIdx = 0
            hitIdx = 1
        else:
            twoWayPlayer = calculatePitchingStats(twoWayPlayer, 1)
            twoWayPlayer = calculateHittingStats(twoWayPlayer, 0)
            pitchIdx = 1
            hitIdx = 0


        return twoWayPlayer, pitchIdx, hitIdx

    except requests.exceptions.HTTPError as errh:
        abort(errh.response.status_code)
