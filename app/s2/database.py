"""Database access for Subsystem 2.

Integrated version: S2 no longer has its own database or its own demo devices.
It uses the one database of the whole project (the devices and buildings come
from Subsystem 1). A separate file can still be given for stand-alone tests.
"""
import sqlite3

from app.db import get_db


def get_connection(database=None):
    """Return the project connection (database=None) or open the given file."""
    if database is None:
        return get_db()
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# Shared SQL: a reading belongs to a device, a device to a building, a building
# to a user. "(? IS NULL OR ...)" means: no filter when the value is None.
FROM_OWN = """
    FROM energy_reading AS r
    JOIN devices   AS d ON d.id = r.device_id
    JOIN buildings AS b ON b.id = d.building_id
"""
WHERE_OWN = " WHERE (? IS NULL OR b.user_id = ?) AND (? IS NULL OR b.id = ?) "


def scope(user_id, building_id):
    """The 4 parameters for WHERE_OWN."""
    return [user_id, user_id, building_id, building_id]
