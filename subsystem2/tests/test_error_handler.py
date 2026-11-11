
"""Tests for Subsystem 2 error handling."""

import pytest

from services.error_handler import (
    EnergyMonitoringError,
    EnergyMonitoringErrorHandler,
)


def test_valid_energy():
    handler = EnergyMonitoringErrorHandler()
    assert handler.validate_energy(12.5) == 12.5


def test_negative_energy():
    handler = EnergyMonitoringErrorHandler()

    with pytest.raises(EnergyMonitoringError):
        handler.validate_energy(-5)


def test_invalid_energy_text():
    handler = EnergyMonitoringErrorHandler()

    with pytest.raises(EnergyMonitoringError):
        handler.validate_energy("invalid")


def test_valid_device_id():
    handler = EnergyMonitoringErrorHandler()
    assert handler.validate_device_id(2) == 2


def test_invalid_device_id():
    handler = EnergyMonitoringErrorHandler()

    with pytest.raises(EnergyMonitoringError):
        handler.validate_device_id(0)

