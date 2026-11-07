from flask import Flask
from .db import init_app as init_db_app, init_db
from .routes import bp

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE="instance/smart_energy.sqlite3",
        SECRET_KEY="local-development-only",
        TESTING=False,
    )
    if test_config:
        app.config.update(test_config)
    database = app.config["DATABASE"]
    if database != ":memory:":
        import os
        parent = os.path.dirname(database)
        if parent:
            os.makedirs(parent, exist_ok=True)
    init_db_app(app)
    with app.app_context():
        init_db()
    app.register_blueprint(bp)
    return app
