# Creates the Flask application (the "application factory").
import os
from flask import Flask, redirect, url_for

from . import db, s1
from .s2 import bp as s2_bp
from .s3 import bp as s3_bp
from .s4 import bp as s4_bp


def load_env_file(path=".env"):
    """Read KEY=value lines from a .env file (if there is one) into the environment.

    This lets the project run without typing the OpenAI key every time.
    Variables that are already set in the environment are not overwritten.
    """
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def create_app(test_config=None):
    if not (test_config and test_config.get("TESTING")):
        load_env_file()
    app = Flask(__name__)

    # Settings. The secret key signs the login cookie: it comes from the
    # environment, not from the code (requirement S1-N7).
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
    app.config["DATABASE"] = os.environ.get("DATABASE", "energy.db")
    if test_config:
        app.config.update(test_config)

    app.teardown_appcontext(db.close_db)
    app.register_blueprint(s1.bp)
    app.register_blueprint(s2_bp)      # energy monitoring + dashboard
    app.register_blueprint(s3_bp)      # cost, carbon, goals, alerts
    app.register_blueprint(s4_bp)      # AI coach + reports

    with app.app_context():
        db.init_db()

    @app.route("/")
    def index():
        return redirect(url_for("monitoring.dashboard"))

    return app
