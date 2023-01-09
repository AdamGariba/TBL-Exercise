from datetime import datetime
import json

from flask import Blueprint, render_template, abort, session
import requests

from ..db import get_db, updateTeamRecords

home_bp = Blueprint('home_bp', __name__)

BASE_URL = "https://statsapi.mlb.com"

@home_bp.route("/")
def index():
    '''
    Returns the Home page view of the application;
    Performs the initial get for standings data and saves the updated data to the database

    Parameters:
        none

    Returns:
        The home view with the necessary data included
    '''
    try:
        db = get_db()
        teams_list = db.execute('SELECT id, abbr FROM team').fetchall()

        teams = {}
        for t in teams_list:
            teams[t['id']] = t['abbr']

        response = requests.get("https://statsapi.mlb.com/api/v1/standings?leagueId=103,104")
        response.raise_for_status()

        results = response.json()

        # If session timestamp is greater than 1 hour update the db
        if "lastUpdated" not in session:
            updateTeamRecords(results['records'][0], db)
            updateTeamRecords(results['records'][1], db)
            updateTeamRecords(results['records'][2], db)
            updateTeamRecords(results['records'][3], db)
            updateTeamRecords(results['records'][4], db)
            updateTeamRecords(results['records'][5], db)

            now = datetime.now()
            session['lastUpdate'] = now.strftime("%d/%m/%Y %H:%M:%S")

        for r in results['records']:
            for t in r['teamRecords']:
                t['team']['abbr'] = teams[t['team']['id']]

        
        # Demonstration of a possible news component
        with open('homebase/home/sampleNews.json', 'r') as f:
            newsList = json.load(f)

        news = newsList['articles'] 


        return render_template("home/index.html", records=results['records'], news=news) 
    except requests.exceptions.HTTPError as errh:
        abort(errh.response.status_code)
