
"""Error handling for Subsystem 2: Energy Monitoring."""


class EnergyMonitoringError(Exception):
    """Base exception for energy monitoring errors."""


class EnergyMonitoringErrorHandler:
    """Validate input data and handle monitoring errors."""

    def __init__(self):
        self.last_error = None

    def validate_energy(self, amount):
        try:
            value = float(amount)
        except (TypeError, ValueError) as error:
            raise EnergyMonitoringError(
                "Energy amount must be a number."
            ) from error

        if not 0 < value < float("inf"):
            raise EnergyMonitoringError(
                "Energy amount must be a finite positive number."
            )

        return value

    def validate_device_id(self, device_id):
        if (
            type(device_id) is not int
            or device_id <= 0
        ):
            raise EnergyMonitoringError(
                "Invalid device ID."
            )

        return device_id

    def handle_error(self, error):
        self.last_error = str(error)
        return {
            "success": False,
            "message": self.last_error
        }
