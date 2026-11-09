# Creates the Flask application (the "application factory").
import os
from flask import Flask, redirect, url_for

from . import db, s1


def create_app(test_config=None):
    app = Flask(__name__)

    # Settings. The secret key signs the login cookie: it comes from the
    # environment, not from the code (requirement S1-N7).
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
    app.config["DATABASE"] = os.environ.get("DATABASE", "energy.db")
    if test_config:
        app.config.update(test_config)

    app.teardown_appcontext(db.close_db)
    app.register_blueprint(s1.bp)

    with app.app_context():
        db.init_db()

    @app.route("/")
    def index():
        return redirect(url_for("s1.buildings"))

    return app
