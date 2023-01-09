import os
from flask import Flask
from datetime import timedelta

def create_app(test_config=None):
    '''
    Sets up an application factory for the flask app.
    Configurations for the app and database are done here

    Parameters:
        test_config: A file containing configurations
    
    Returns:
        Configured app
    '''
    app = Flask(__name__)
    app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'homebase.sqlite'),
    )

    app.config.update(
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=60)
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register database here
    from . import db
    db.init_app(app)

    # Register blueprints here
    from .home.routes import home_bp 
    app.register_blueprint(home_bp)

    from .team.routes import team_bp
    app.register_blueprint(team_bp)

    from .player.routes import player_bp
    app.register_blueprint(player_bp)

    return app
