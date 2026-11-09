# Database helper: opens the SQLite file and creates the tables.
import sqlite3
from flask import current_app, g


def get_db():
    """Return the database connection of the current request (opens it once)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row          # rows can be read like row["name"]
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    """Close the connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the tables from schema.sql (does nothing if they already exist)."""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))
    db.commit()
