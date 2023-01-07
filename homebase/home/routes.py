from flask import Blueprint, render_template, abort
import requests

from ..db import get_db

home_bp = Blueprint('home_bp', __name__)

BASE_URL = "https://statsapi.mlb.com"

@home_bp.route("/")
def index():
    try:
        db = get_db()
        teams_list = db.execute('SELECT * FROM team').fetchall()

        teams = {}
        for t in teams_list:
            teams[t['id']] = t['abbr']

        response = requests.get("https://statsapi.mlb.com/api/v1/standings?leagueId=103,104")
        response.raise_for_status()

        results = response.json()

        for r in results['records']:
            for t in r['teamRecords']:
                t['team']['abbr'] = teams[t['team']['id']]


        return render_template("home/index.html", records=results['records']) 
    except requests.exceptions.HTTPError as errh:
        abort(errh.response.status_code)
