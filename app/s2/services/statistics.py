"""Statistics class for Subsystem 2."""

from app.s2.services.energy_calculator import (
    get_daily_totals,
    get_weekly_totals,
    get_monthly_totals,
    get_total_consumption,
    get_reading_count,
    get_device_count,
)


class Statistics:
    """Calculate energy consumption statistics.

    user_id / building_id limit the numbers to one user / one building.
    database=None means: use the database of the whole project.
    """

    def __init__(self, database=None, user_id=None, building_id=None):
        self.initialize(database, user_id, building_id)

    def initialize(self, database, user_id=None, building_id=None):
        self.set_database(database)
        self._user_id = user_id
        self._building_id = building_id

    def get_database(self):
        return self._database

    def set_database(self, value):
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError("Database path must not be empty.")
        self._database = value

    def _args(self):
        return dict(user_id=self._user_id, building_id=self._building_id,
                    database=self._database)

    def total_per_day(self):
        return get_daily_totals(**self._args())

    def total_per_week(self):
        return get_weekly_totals(**self._args())

    def total_per_month(self):
        return get_monthly_totals(**self._args())

    def total_consumption(self):
        return get_total_consumption(**self._args())

    def reading_count(self):
        return get_reading_count(**self._args())

    def device_count(self):
        return get_device_count(**self._args())
