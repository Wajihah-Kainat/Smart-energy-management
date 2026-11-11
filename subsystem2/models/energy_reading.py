
"""Database operations for S2 energy readings."""

from datetime import date
from database import get_connection


def list_readings(database="energy.db"):
    """Return all energy readings with their device names."""
    with get_connection(database) as connection:
        return connection.execute("""
            SELECT r.id, r.device_id, d.name AS device_name,
                   r.date, r.amount_kwh, r.is_simulated
            FROM energy_reading AS r
            JOIN demo_devices AS d ON d.id = r.device_id
            ORDER BY r.date DESC, r.id DESC
        """).fetchall()


def add_reading(device_id, reading_date, amount_kwh,
                is_simulated=False, database="energy.db"):
    """Add a new energy reading to the database."""

    if not isinstance(device_id, int) or device_id <= 0:
        raise ValueError("Invalid device ID.")

    try:
        date.fromisoformat(reading_date)
    except (ValueError, TypeError):
        raise ValueError("Date must use YYYY-MM-DD format.")

    try:
        amount_kwh = float(amount_kwh)
    except (ValueError, TypeError):
        raise ValueError("Energy amount must be a number.")

    if amount_kwh <= 0:
        raise ValueError("Energy amount must be positive.")

    with get_connection(database) as connection:
        device = connection.execute(
            "SELECT id FROM demo_devices WHERE id = ?",
            (device_id,)
        ).fetchone()

        if device is None:
            raise ValueError("Device does not exist.")

        cursor = connection.execute("""
            INSERT INTO energy_reading
                (device_id, date, amount_kwh, is_simulated)
            VALUES (?, ?, ?, ?)
        """, (device_id, reading_date, amount_kwh, int(is_simulated)))

        return cursor.lastrowid


def update_reading(reading_id, device_id, reading_date,
                   amount_kwh, database="energy.db"):
    """Update an existing energy reading."""

    if not isinstance(reading_id, int) or reading_id <= 0:
        raise ValueError("Invalid reading ID.")

    if not isinstance(device_id, int) or device_id <= 0:
        raise ValueError("Invalid device ID.")

    try:
        date.fromisoformat(reading_date)
        amount_kwh = float(amount_kwh)
    except (ValueError, TypeError):
        raise ValueError("Invalid date or energy amount.")

    if amount_kwh <= 0:
        raise ValueError("Energy amount must be positive.")

    with get_connection(database) as connection:
        device = connection.execute(
            "SELECT id FROM demo_devices WHERE id = ?",
            (device_id,)
        ).fetchone()

        if device is None:
            raise ValueError("Device does not exist.")

        cursor = connection.execute("""
            UPDATE energy_reading
            SET device_id = ?, date = ?, amount_kwh = ?
            WHERE id = ?
        """, (device_id, reading_date, amount_kwh, reading_id))

        if cursor.rowcount == 0:
            raise ValueError("Reading does not exist.")

        return True


def delete_reading(reading_id, database="energy.db"):
    """Delete an energy reading by its ID."""

    if not isinstance(reading_id, int) or reading_id <= 0:
        raise ValueError("Invalid reading ID.")

    with get_connection(database) as connection:
        cursor = connection.execute(
            "DELETE FROM energy_reading WHERE id = ?",
            (reading_id,)
        )

        if cursor.rowcount == 0:
            raise ValueError("Reading does not exist.")

        return True
