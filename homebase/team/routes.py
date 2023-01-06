import copy
from flask import Blueprint, abort, render_template
import requests

team_bp = Blueprint('team_bp', __name__)

@team_bp.route('/team/<team_id>')
def teamDetails(team_id):
    try:
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


        return render_template('team/team_details.html', pitchers=pitchers, hitters=hitters)
    except requests.exceptions.HTTPError as errh:
        abort(errh.response.status_code)


def calculatePitchingStats(pitcher, statIndex):
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
    try:
        tw_req = requests.get(f"https://statsapi.mlb.com/api/v1/people/{playerId}?hydrate=stats(group=[hitting,pitching],type=[season])")
        tw_req.raise_for_status()
        
        result = tw_req.json()

        twoWayPlayer = result['people'][0]

        pitchIdx = 0
        hitIdx = 0

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
