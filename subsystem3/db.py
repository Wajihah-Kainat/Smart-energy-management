import sqlite3
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS energy_settings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id INTEGER NOT NULL,
  building_id INTEGER NOT NULL,
  price_per_kwh REAL NOT NULL CHECK(price_per_kwh >= 0),
  emission_factor REAL NOT NULL CHECK(emission_factor >= 0),
  factor_source TEXT NOT NULL,
  UNIQUE(owner_id, building_id)
);
CREATE TABLE IF NOT EXISTS energy_readings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id INTEGER NOT NULL,
  building_id INTEGER NOT NULL,
  reading_date TEXT NOT NULL,
  amount_kwh REAL NOT NULL CHECK(amount_kwh >= 0),
  is_simulated INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_readings_owner_building_date
  ON energy_readings(owner_id, building_id, reading_date);
CREATE TABLE IF NOT EXISTS energy_goals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id INTEGER NOT NULL,
  building_id INTEGER NOT NULL,
  target_kwh REAL NOT NULL CHECK(target_kwh > 0),
  month TEXT NOT NULL,
  daily_limit_kwh REAL NOT NULL CHECK(daily_limit_kwh > 0),
  UNIQUE(owner_id, building_id, month)
);
CREATE TABLE IF NOT EXISTS energy_alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id INTEGER NOT NULL,
  building_id INTEGER NOT NULL,
  message TEXT NOT NULL,
  created_at TEXT NOT NULL,
  is_read INTEGER NOT NULL DEFAULT 0
);
"""

def get_db():
    if "db" not in g:
        path = current_app.config["DATABASE"]
        if path == ":memory:":
            # Shared in-memory connection for the lifetime of the app context.
            conn = sqlite3.connect(":memory:")
        else:
            conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db

def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()

def init_app(app):
    app.teardown_appcontext(close_db)
