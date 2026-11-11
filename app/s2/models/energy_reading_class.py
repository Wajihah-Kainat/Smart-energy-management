
from datetime import date


class EnergyReading:
    """Represents one energy consumption reading."""

    def __init__(
        self,
        reading_id,
        device_id,
        reading_date,
        amount_kwh,
        is_simulated=False,
    ):
        self.initialize(
            reading_id,
            device_id,
            reading_date,
            amount_kwh,
            is_simulated,
        )

    def initialize(
        self,
        reading_id,
        device_id,
        reading_date,
        amount_kwh,
        is_simulated=False,
    ):
        self.set_id(reading_id)
        self.set_device_id(device_id)
        self.set_date(reading_date)
        self.set_amount_kwh(amount_kwh)
        self.set_is_simulated(is_simulated)

    def get_id(self):
        return self._id

    def set_id(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Invalid reading ID.")
        self._id = value

    def get_device_id(self):
        return self._device_id

    def set_device_id(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Invalid device ID.")
        self._device_id = value

    def get_date(self):
        return self._date

    def set_date(self, value):
        if not isinstance(value, str):
            raise ValueError("Date must be a string.")

        date.fromisoformat(value)
        self._date = value

    def get_amount_kwh(self):
        return self._amount_kwh

    def set_amount_kwh(self, value):
        value = float(value)
        if value <= 0:
            raise ValueError("Energy amount must be positive.")
        self._amount_kwh = value

    def get_is_simulated(self):
        return self._is_simulated

    def set_is_simulated(self, value):
        if not isinstance(value, bool):
            raise ValueError("Simulation flag must be boolean.")
        self._is_simulated = value

