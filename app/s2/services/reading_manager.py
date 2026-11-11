
"""Reading management class for Subsystem 2."""

from app.s2.models.energy_reading import (
    list_readings,
    add_reading,
    update_reading,
    delete_reading,
)


class ReadingManager:
    """Manage energy readings using the existing database functions."""

    def __init__(self, database=None, user_id=None):
        self.initialize(database, user_id)

    def initialize(self, database, user_id=None):
        self.set_database(database)
        self._user_id = user_id

    def get_database(self):
        return self._database

    def set_database(self, value):
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError("Database path must not be empty.")
        self._database = value

    def list_all(self):
        return list_readings(user_id=self._user_id, database=self._database)

    def add(self, device_id, reading_date, amount_kwh,
            is_simulated=False):
        return add_reading(
            device_id,
            reading_date,
            amount_kwh,
            is_simulated,
            user_id=self._user_id,
            database=self._database,
        )

    def edit(self, reading_id, device_id, reading_date, amount_kwh):
        return update_reading(
            reading_id,
            device_id,
            reading_date,
            amount_kwh,
            user_id=self._user_id,
            database=self._database,
        )

    def delete(self, reading_id):
        return delete_reading(
            reading_id,
            user_id=self._user_id,
            database=self._database,
        )

    def filter_by_date(self, date_from, date_to):
        """Return readings within the selected date range."""
        from datetime import date

        start = date.fromisoformat(date_from)
        end = date.fromisoformat(date_to)

        if start > end:
            raise ValueError("Start date must not be after end date.")

        readings = self.list_all()

        return [
            reading for reading in readings
            if start <= date.fromisoformat(reading["date"]) <= end
        ]

    def simulate_live(self, device_id):
        """Create one simulated energy reading."""
        import random
        from datetime import date

        amount_kwh = round(random.uniform(0.2, 2.0), 2)
        reading_date = date.today().isoformat()

        return self.add(
            device_id=device_id,
            reading_date=reading_date,
            amount_kwh=amount_kwh,
            is_simulated=True,
        )
