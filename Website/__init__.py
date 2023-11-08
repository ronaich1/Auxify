# this file is for automatically initializing your app
from flask import Flask, session
# local files import here
from .views import views


def create_app():
    app = Flask(__name__)
    app.config["SESSION_COOKIE_NAME"] = "Spotify Cookie"
    app.secret_key = "UNGUESSABLE"

    # register the blueprints
    app.register_blueprint(views, url_prefix='/')

    return app
