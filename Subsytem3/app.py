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