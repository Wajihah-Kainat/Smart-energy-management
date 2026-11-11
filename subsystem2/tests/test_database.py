import sqlite3
from database import init_db, get_connection

def test_database_creates_demo_devices_and_readings_table(tmp_path):
    db = tmp_path / "test_energy.db"
    init_db(str(db))
    with get_connection(str(db)) as connection:
        devices = connection.execute("SELECT COUNT(*) FROM demo_devices").fetchone()[0]
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='energy_reading'"
        ).fetchone()
    assert devices == 3
    assert tables is not None

def test_reading_rejects_non_positive_energy(tmp_path):
    db = tmp_path / "test_energy.db"
    init_db(str(db))
    with get_connection(str(db)) as connection:
        try:
            connection.execute(
                "INSERT INTO energy_reading (device_id, date, amount_kwh) VALUES (1, '2026-11-01', 0)"
            )
            assert False, "Expected CHECK constraint to reject zero kWh"
        except sqlite3.IntegrityError:
            pass
