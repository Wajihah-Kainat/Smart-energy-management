import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;

-- Temporary demo table. In the integrated project, this will be
-- replaced by / connected to the Device table owned by Subsystem 1.
CREATE TABLE IF NOT EXISTS demo_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    energy_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS energy_reading (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    amount_kwh REAL NOT NULL CHECK (amount_kwh > 0),
    is_simulated INTEGER NOT NULL DEFAULT 0
        CHECK (is_simulated IN (0, 1)),
    FOREIGN KEY (device_id) REFERENCES demo_devices(id)
);

CREATE INDEX IF NOT EXISTS idx_reading_date
    ON energy_reading(date);
CREATE INDEX IF NOT EXISTS idx_reading_device
    ON energy_reading(device_id);
"""

def get_connection(database="energy.db"):
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def init_db(database="energy.db"):
    Path(database).parent.mkdir(parents=True, exist_ok=True) if str(database) not in (":memory:", "") else None
    with get_connection(database) as connection:
        connection.executescript(SCHEMA)
        count = connection.execute(
            "SELECT COUNT(*) FROM demo_devices"
        ).fetchone()[0]
        if count == 0:
            connection.executemany(
                "INSERT INTO demo_devices (name, energy_type) VALUES (?, ?)",
                [
                    ("Air Conditioner", "Electricity"),
                    ("Refrigerator", "Electricity"),
                    ("Lighting", "Electricity"),
                ],
            )
