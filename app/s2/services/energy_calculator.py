"""Energy totals for Subsystem 2 (all numbers come from the stored readings).

user_id / building_id limit the totals to one user / one building (None = all).
"""

from app.s2.database import FROM_OWN, WHERE_OWN, get_connection, scope


def _rows(select_group, user_id, building_id, database):
    with get_connection(database) as connection:
        return connection.execute(
            select_group.replace("{from_where}", FROM_OWN + WHERE_OWN),
            scope(user_id, building_id)).fetchall()


def get_daily_totals(user_id=None, building_id=None, database=None):
    """Return total energy consumption for each day."""
    return _rows("""
        SELECT r.date AS date, ROUND(SUM(r.amount_kwh), 2) AS total_kwh
        {from_where}
        GROUP BY r.date ORDER BY r.date ASC
    """, user_id, building_id, database)


def get_weekly_totals(user_id=None, building_id=None, database=None):
    """Return total energy consumption grouped by year/week."""
    return _rows("""
        SELECT strftime('%Y-W%W', r.date) AS period, ROUND(SUM(r.amount_kwh), 2) AS total_kwh
        {from_where}
        GROUP BY strftime('%Y-W%W', r.date) ORDER BY MIN(r.date) ASC
    """, user_id, building_id, database)


def get_monthly_totals(user_id=None, building_id=None, database=None):
    """Return total energy consumption grouped by month."""
    return _rows("""
        SELECT strftime('%Y-%m', r.date) AS period, ROUND(SUM(r.amount_kwh), 2) AS total_kwh
        {from_where}
        GROUP BY strftime('%Y-%m', r.date) ORDER BY period ASC
    """, user_id, building_id, database)


def get_total_consumption(user_id=None, building_id=None, database=None):
    """Return total consumption across all readings."""
    row = _rows("""
        SELECT ROUND(COALESCE(SUM(r.amount_kwh), 0), 2) AS total_kwh {from_where}
    """, user_id, building_id, database)[0]
    return row["total_kwh"]


def get_reading_count(user_id=None, building_id=None, database=None):
    """Return number of stored energy readings."""
    row = _rows("SELECT COUNT(*) AS count {from_where}", user_id, building_id, database)[0]
    return row["count"]


def get_device_count(user_id=None, building_id=None, database=None):
    """Number of devices registered in Subsystem 1."""
    with get_connection(database) as connection:
        return connection.execute(
            "SELECT COUNT(*) FROM devices AS d JOIN buildings AS b ON b.id = d.building_id "
            "WHERE (? IS NULL OR b.user_id = ?) AND (? IS NULL OR b.id = ?)",
            scope(user_id, building_id)).fetchone()[0]
