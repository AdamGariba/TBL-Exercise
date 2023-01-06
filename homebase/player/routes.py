from flask import Blueprint, abort, render_template
import requests

player_bp = Blueprint('player_bp', __name__)

@player_bp.route('/player/<player_id>')
def playerDetails(player_id):
    return f"Hello player {player_id}"
