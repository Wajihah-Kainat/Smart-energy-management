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
