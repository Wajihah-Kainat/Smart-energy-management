
"""Statistics class for Subsystem 2."""

from services.energy_calculator import (
    get_daily_totals,
    get_weekly_totals,
    get_monthly_totals,
    get_total_consumption,
    get_reading_count,
)


class Statistics:
    """Calculate energy consumption statistics."""

    def __init__(self, database="energy.db"):
        self.initialize(database)

    def initialize(self, database):
        self.set_database(database)

    def get_database(self):
        return self._database

    def set_database(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Database path must not be empty.")
        self._database = value

    def total_per_day(self):
        return get_daily_totals(database=self._database)

    def total_per_week(self):
        return get_weekly_totals(database=self._database)

    def total_per_month(self):
        return get_monthly_totals(database=self._database)

    def total_consumption(self):
        return get_total_consumption(database=self._database)

    def reading_count(self):
        return get_reading_count(database=self._database)
