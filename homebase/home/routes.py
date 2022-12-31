from flask import Blueprint, render_template
import requests

home_bp = Blueprint('home_bp', __name__)

@home_bp.route("/")
def index():
    try:
        response = requests.get("https://statsapi.mlb.com/api/v1/standings?leagueId=103,104")
        response.raise_for_status()

        results = response.json()
        return render_template("home/index.html", records=results['records']) 
    except requests.exceptions.HTTPError as errh:
        print(errh)
