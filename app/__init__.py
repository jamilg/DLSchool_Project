from flask import Flask
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap
from flask_debug import Debug

from app.frontend import frontend
from app import forms
from app.nav import nav


def create_app(configfile=None):
    app = Flask(__name__, template_folder='templates')

    AppConfig(app)

    # Install our Bootstrap extension
    Bootstrap(app)

    # For debugging (there will be errors without it)
    Debug(app)

    # Our application uses blueprints as well; these go well with the
    # application factory. We already imported the blueprint, now we just need
    # to register it:
    app.register_blueprint(frontend)

    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    app.secret_key = 'try_to_guess'

    # We initialize the navigation as well
    nav.init_app(app)

    return app
