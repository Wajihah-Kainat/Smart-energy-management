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
        self.set_building_id(building_id)
        self.set_price_per_kwh(price_per_kwh)
        self.set_emission_factor(emission_factor)
        self.set_factor_source(factor_source)

    def get_building_id(self): return self._building_id
    def set_building_id(self, value):
        self._building_id = value

    def get_price_per_kwh(self): return self._price_per_kwh
    def set_price_per_kwh(self, value):
        self._price_per_kwh = value
    def get_emission_factor(self): return self._emission_factor
    def set_emission_factor(self, value):
        self._emission_factor = value

    def get_factor_source(self): return self._factor_source
    def set_factor_source(self, value):
        self._factor_source = value

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
        self._energy_kwh = value

    def get_settings(self): return self._settings
    def set_settings(self, value):
        self._settings = value

    def get_period(self): return self._period
    def set_period(self, value):
        if value not in self.VALID_PERIODS:
            raise ValueError("period must be day, week, or month.")
        self._period = value

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
    def set_target_kwh(self, value): self._target_kwh = value

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
        self._daily_limit_kwh = value

    def calculate_progress(self, consumed_kwh: float) -> float:
        consumed = consumed_kwh
        if self._target_kwh is None or self._target_kwh <= 0:
            raise ValueError("target_kwh must be greater than zero.")
        return round(consumed / self._target_kwh * 100, 2)

    def is_daily_limit_exceeded(self, daily_kwh: float) -> bool:
        if self._daily_limit_kwh is None:
            raise ValueError("daily_limit_kwh must be set.")
        return daily_kwh > self._daily_limit_kwh