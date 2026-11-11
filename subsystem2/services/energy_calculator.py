"""Energy statistics for Subsystem 2."""

from database import get_connection


def get_daily_totals(database="energy.db"):
    """Return total energy consumption for each day."""
    with get_connection(database) as connection:
        return connection.execute("""
            SELECT
                date,
                ROUND(SUM(amount_kwh), 2) AS total_kwh
            FROM energy_reading
            GROUP BY date
            ORDER BY date ASC
        """).fetchall()


def get_weekly_totals(database="energy.db"):
    """Return total energy consumption grouped by year/week."""
    with get_connection(database) as connection:
        return connection.execute("""
            SELECT
                strftime('%Y-W%W', date) AS period,
                ROUND(SUM(amount_kwh), 2) AS total_kwh
            FROM energy_reading
            GROUP BY strftime('%Y-W%W', date)
            ORDER BY MIN(date) ASC
        """).fetchall()


def get_monthly_totals(database="energy.db"):
    """Return total energy consumption grouped by month."""
    with get_connection(database) as connection:
        return connection.execute("""
            SELECT
                strftime('%Y-%m', date) AS period,
                ROUND(SUM(amount_kwh), 2) AS total_kwh
            FROM energy_reading
            GROUP BY strftime('%Y-%m', date)
            ORDER BY period ASC
        """).fetchall()


def get_total_consumption(database="energy.db"):
    """Return total consumption across all readings."""
    with get_connection(database) as connection:
        result = connection.execute("""
            SELECT
                ROUND(COALESCE(SUM(amount_kwh), 0), 2)
                AS total_kwh
            FROM energy_reading
        """).fetchone()

        return result["total_kwh"]


def get_reading_count(database="energy.db"):
    """Return number of stored energy readings."""
    with get_connection(database) as connection:
        result = connection.execute("""
            SELECT COUNT(*) AS count
            FROM energy_reading
        """).fetchone()

        return result["count"]