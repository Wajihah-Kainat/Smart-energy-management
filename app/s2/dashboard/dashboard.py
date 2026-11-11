
"""Dashboard class for Subsystem 2."""

import csv
import io

from app.s2.models.energy_reading import list_readings
from app.s2.services.statistics import Statistics


class Dashboard:
    """Prepare energy data for charts and CSV export."""

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

    def chart_data(self):
        statistics = Statistics(self._database, self._user_id, self._building_id)

        return {
            "daily": [
                dict(row)
                for row in statistics.total_per_day()
            ],
            "weekly": [
                dict(row)
                for row in statistics.total_per_week()
            ],
            "monthly": [
                dict(row)
                for row in statistics.total_per_month()
            ],
        }

    def export_csv(self):
        readings = list_readings(user_id=self._user_id, building_id=self._building_id,
                                 database=self._database)

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "ID",
            "Device",
            "Date",
            "Consumption (kWh)",
            "Type",
        ])

        for reading in readings:
            writer.writerow([
                reading["id"],
                reading["device_name"],
                reading["date"],
                reading["amount_kwh"],
                "Simulated" if reading["is_simulated"] else "Real",
            ])

        return output.getvalue()
