"""Database operations for S2 energy readings.

Every function can be limited to one user (user_id). The routes always pass the
logged-in user, so nobody can see or change readings of another user (rule S1-N3).
"""

from datetime import date

from app.s2.database import FROM_OWN, WHERE_OWN, get_connection, scope


def list_readings(user_id=None, building_id=None, device_id=None,
                  date_from=None, date_to=None, database=None):
    """Return the readings (newest first) with device and building name."""
    query = ("SELECT r.id, r.device_id, d.name AS device_name, b.name AS building_name,"
             " r.date, r.amount_kwh, r.is_simulated " + FROM_OWN + WHERE_OWN)
    parameters = scope(user_id, building_id)
    if device_id:
        query += " AND r.device_id = ?"
        parameters.append(int(device_id))
    if date_from:
        query += " AND r.date >= ?"
        parameters.append(date_from)
    if date_to:
        query += " AND r.date <= ?"
        parameters.append(date_to)
    query += " ORDER BY r.date DESC, r.id DESC"
    with get_connection(database) as connection:
        return connection.execute(query, parameters).fetchall()


def list_devices(user_id=None, building_id=None, database=None):
    """Devices (from Subsystem 1) on which a reading can be recorded."""
    with get_connection(database) as connection:
        return connection.execute(
            "SELECT d.id, d.name, b.name AS building_name, b.id AS building_id "
            "FROM devices AS d JOIN buildings AS b ON b.id = d.building_id "
            "WHERE (? IS NULL OR b.user_id = ?) AND (? IS NULL OR b.id = ?) "
            "ORDER BY b.name, d.name", scope(user_id, building_id)).fetchall()


def _check_device(connection, device_id, user_id):
    device = connection.execute(
        "SELECT d.id FROM devices AS d JOIN buildings AS b ON b.id = d.building_id "
        "WHERE d.id = ? AND (? IS NULL OR b.user_id = ?)",
        (device_id, user_id, user_id)).fetchone()
    if device is None:
        raise ValueError("Device does not exist.")


def add_reading(device_id, reading_date, amount_kwh, is_simulated=False,
                user_id=None, database=None):
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

    if not 0 < amount_kwh < float("inf"):
        raise ValueError("Energy amount must be positive.")

    with get_connection(database) as connection:
        _check_device(connection, device_id, user_id)
        cursor = connection.execute(
            "INSERT INTO energy_reading (device_id, date, amount_kwh, is_simulated) "
            "VALUES (?, ?, ?, ?)", (device_id, reading_date, amount_kwh, int(is_simulated)))
        return cursor.lastrowid


def get_reading(reading_id, user_id=None, database=None):
    """Return one reading (or None if it does not exist or is not yours)."""
    with get_connection(database) as connection:
        return connection.execute(
            "SELECT r.id, r.device_id, r.date, r.amount_kwh " + FROM_OWN +
            "WHERE r.id = ? AND (? IS NULL OR b.user_id = ?)",
            (reading_id, user_id, user_id)).fetchone()


def update_reading(reading_id, device_id, reading_date, amount_kwh,
                   user_id=None, database=None):
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

    if not 0 < amount_kwh < float("inf"):
        raise ValueError("Energy amount must be positive.")

    if get_reading(reading_id, user_id, database) is None:
        raise ValueError("Reading does not exist.")

    with get_connection(database) as connection:
        _check_device(connection, device_id, user_id)
        connection.execute(
            "UPDATE energy_reading SET device_id = ?, date = ?, amount_kwh = ? WHERE id = ?",
            (device_id, reading_date, amount_kwh, reading_id))
        return True


def delete_reading(reading_id, user_id=None, database=None):
    """Delete an energy reading by its ID."""

    if not isinstance(reading_id, int) or reading_id <= 0:
        raise ValueError("Invalid reading ID.")

    if get_reading(reading_id, user_id, database) is None:
        raise ValueError("Reading does not exist.")

    with get_connection(database) as connection:
        connection.execute("DELETE FROM energy_reading WHERE id = ?", (reading_id,))
        return True
