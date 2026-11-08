"""Object-oriented domain classes for Subsystem 3.

These classes are framework-independent. Constructors initialize state; initialize_* methods
make configuration/setup explicit; getters/setters encapsulate state and validate inputs.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional


def _positive_number(value, field_name, allow_zero=False):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a number.")
    if number < 0 or (number == 0 and not allow_zero):
        qualifier = "zero or greater" if allow_zero else "greater than zero"
        raise ValueError(f"{field_name} must be {qualifier}.")
    return number


class EnergySettings:
    """Configuration for energy price and carbon emission factor."""

    def __init__(self, building_id: int, price_per_kwh: float,
                 emission_factor: float, factor_source: str):
        self._building_id = None
        self._price_per_kwh = None
        self._emission_factor = None
        self._factor_source = ""
        self.initialize(building_id, price_per_kwh, emission_factor, factor_source)

    def initialize(self, building_id, price_per_kwh, emission_factor, factor_source):
        if not isinstance(building_id, int) or building_id <= 0:
            raise ValueError("building_id must be a positive integer.")
        self.set_building_id(building_id)
        self.set_price_per_kwh(price_per_kwh)
        self.set_emission_factor(emission_factor)
        self.set_factor_source(factor_source)

    def get_building_id(self): return self._building_id
    def set_building_id(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("building_id must be a positive integer.")
        self._building_id = value

    def get_price_per_kwh(self): return self._price_per_kwh
    def set_price_per_kwh(self, value):
        self._price_per_kwh = _positive_number(value, "price_per_kwh", allow_zero=True)

    def get_emission_factor(self): return self._emission_factor
    def set_emission_factor(self, value):
        self._emission_factor = _positive_number(value, "emission_factor", allow_zero=True)

    def get_factor_source(self): return self._factor_source
    def set_factor_source(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("factor_source is required.")
        self._factor_source = value.strip()


class EnergyAnalytics:
    """Calculates cost and carbon for an energy quantity and period."""

    VALID_PERIODS = {"day", "week", "month"}

    def __init__(self, energy_kwh: float, settings: EnergySettings, period: str = "month"):
        self._energy_kwh = 0.0
        self._settings = None
        self._period = "month"
        self.initialize(energy_kwh, settings, period)

    def initialize(self, energy_kwh, settings, period):
        self.set_energy_kwh(energy_kwh)
        self.set_settings(settings)
        self.set_period(period)

    def get_energy_kwh(self): return self._energy_kwh
    def set_energy_kwh(self, value):
        self._energy_kwh = _positive_number(value, "energy_kwh", allow_zero=True)

    def get_settings(self): return self._settings
    def set_settings(self, value):
        if not isinstance(value, EnergySettings):
            raise TypeError("settings must be an EnergySettings instance.")
        self._settings = value

    def get_period(self): return self._period
    def set_period(self, value):
        if value not in self.VALID_PERIODS:
            raise ValueError("period must be day, week, or month.")
        self._period = value

    def calculate_cost(self) -> float:
        """Cost = kWh × configured currency price per kWh."""
        return round(self._energy_kwh * self._settings.get_price_per_kwh(), 2)

    def calculate_carbon_emissions(self) -> float:
        """Carbon kg CO2 = kWh × emission factor (kg CO2/kWh)."""
        return round(self._energy_kwh * self._settings.get_emission_factor(), 2)


class SustainabilityScore:
    """Transparent, adjustable MVP sustainability score in the range 0–100."""

    def __init__(self, current_energy_kwh: float, monthly_target_kwh: float,
                 current_carbon_kg: float, previous_carbon_kg: Optional[float] = None):
        self._current_energy_kwh = 0.0
        self._monthly_target_kwh = 1.0
        self._current_carbon_kg = 0.0
        self._previous_carbon_kg = None
        self._score = 0.0
        self.initialize(current_energy_kwh, monthly_target_kwh, current_carbon_kg, previous_carbon_kg)

    def initialize(self, current_energy_kwh, monthly_target_kwh, current_carbon_kg, previous_carbon_kg=None):
        self.set_current_energy_kwh(current_energy_kwh)
        self.set_monthly_target_kwh(monthly_target_kwh)
        self.set_current_carbon_kg(current_carbon_kg)
        self.set_previous_carbon_kg(previous_carbon_kg)

    def get_current_energy_kwh(self): return self._current_energy_kwh
    def set_current_energy_kwh(self, value):
        self._current_energy_kwh = _positive_number(value, "current_energy_kwh", allow_zero=True)

    def get_monthly_target_kwh(self): return self._monthly_target_kwh
    def set_monthly_target_kwh(self, value):
        self._monthly_target_kwh = _positive_number(value, "monthly_target_kwh")

    def get_current_carbon_kg(self): return self._current_carbon_kg
    def set_current_carbon_kg(self, value):
        self._current_carbon_kg = _positive_number(value, "current_carbon_kg", allow_zero=True)

    def get_previous_carbon_kg(self): return self._previous_carbon_kg
    def set_previous_carbon_kg(self, value):
        self._previous_carbon_kg = None if value is None else _positive_number(value, "previous_carbon_kg", allow_zero=True)

    def get_score(self): return self._score
    def set_score(self, value):
        number = float(value)
        if not 0 <= number <= 100:
            raise ValueError("score must be between 0 and 100.")
        self._score = round(number, 2)

    def calculate_score(self) -> float:
        # Up to 70 points for staying within target; up to 30 for carbon reduction.
        usage_points = max(0.0, 70.0 * (1.0 - self._current_energy_kwh / self._monthly_target_kwh))
        if self._previous_carbon_kg is None:
            carbon_points = 15.0  # neutral baseline when comparison data is unavailable
        elif self._previous_carbon_kg == 0:
            carbon_points = 30.0 if self._current_carbon_kg == 0 else 0.0
        else:
            reduction = (self._previous_carbon_kg - self._current_carbon_kg) / self._previous_carbon_kg
            carbon_points = max(0.0, min(30.0, 30.0 * reduction))
        self.set_score(max(0.0, min(100.0, usage_points + carbon_points)))
        return self._score


class EnergyGoal:
    """Monthly kWh target and daily alert threshold."""

    def __init__(self, owner_id: int, building_id: int, target_kwh: float,
                 month: str, daily_limit_kwh: float):
        self._owner_id = None
        self._building_id = None
        self._target_kwh = None
        self._month = ""
        self._daily_limit_kwh = None
        self.initialize(owner_id, building_id, target_kwh, month, daily_limit_kwh)

    def initialize(self, owner_id, building_id, target_kwh, month, daily_limit_kwh):
        for name, value in (("owner_id", owner_id), ("building_id", building_id)):
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer.")
        self.set_owner_id(owner_id)
        self.set_building_id(building_id)
        self.set_target_kwh(target_kwh)
        self.set_month(month)
        self.set_daily_limit_kwh(daily_limit_kwh)

    def get_owner_id(self): return self._owner_id
    def set_owner_id(self, value):
        if not isinstance(value, int) or value <= 0: raise ValueError("owner_id must be positive.")
        self._owner_id = value

    def get_building_id(self): return self._building_id
    def set_building_id(self, value):
        if not isinstance(value, int) or value <= 0: raise ValueError("building_id must be positive.")
        self._building_id = value

    def get_target_kwh(self): return self._target_kwh
    def set_target_kwh(self, value): self._target_kwh = _positive_number(value, "target_kwh")

    def get_month(self): return self._month
    def set_month(self, value):
        try:
            year, month = value.split("-")
            if len(year) != 4 or not 1 <= int(month) <= 12: raise ValueError
        except (AttributeError, ValueError):
            raise ValueError("month must use YYYY-MM format.")
        self._month = value

    def get_daily_limit_kwh(self): return self._daily_limit_kwh
    def set_daily_limit_kwh(self, value):
        self._daily_limit_kwh = _positive_number(value, "daily_limit_kwh")

    def calculate_progress(self, consumed_kwh: float) -> float:
        consumed = _positive_number(consumed_kwh, "consumed_kwh", allow_zero=True)
        return round(consumed / self._target_kwh * 100, 2)

    def is_daily_limit_exceeded(self, daily_kwh: float) -> bool:
        return _positive_number(daily_kwh, "daily_kwh", allow_zero=True) > self._daily_limit_kwh


class EnergyAlert:
    """An alert belonging to a user/building; database persistence is handled by services."""

    def __init__(self, owner_id: int, building_id: int, message: str,
                 created_at: Optional[str] = None, is_read: bool = False):
        self._owner_id = None
        self._building_id = None
        self._message = ""
        self._created_at = created_at or date.today().isoformat()
        self._is_read = False
        self.initialize(owner_id, building_id, message, self._created_at, is_read)

    def initialize(self, owner_id, building_id, message, created_at=None, is_read=False):
        if not isinstance(owner_id, int) or owner_id <= 0: raise ValueError("owner_id must be positive.")
        if not isinstance(building_id, int) or building_id <= 0: raise ValueError("building_id must be positive.")
        self.set_owner_id(owner_id)
        self.set_building_id(building_id)
        self.set_message(message)
        self.set_created_at(created_at or date.today().isoformat())
        self.set_is_read(is_read)

    def get_owner_id(self): return self._owner_id
    def set_owner_id(self, value):
        if not isinstance(value, int) or value <= 0: raise ValueError("owner_id must be positive.")
        self._owner_id = value

    def get_building_id(self): return self._building_id
    def set_building_id(self, value):
        if not isinstance(value, int) or value <= 0: raise ValueError("building_id must be positive.")
        self._building_id = value

    def get_message(self): return self._message
    def set_message(self, value):
        if not isinstance(value, str) or not value.strip(): raise ValueError("message is required.")
        self._message = value.strip()

    def get_created_at(self): return self._created_at
    def set_created_at(self, value):
        if not isinstance(value, str) or not value.strip(): raise ValueError("created_at is required.")
        self._created_at = value.strip()

    def get_is_read(self): return self._is_read
    def set_is_read(self, value):
        if not isinstance(value, bool): raise ValueError("is_read must be a boolean.")
        self._is_read = value

    def mark_read(self): self.set_is_read(True)
