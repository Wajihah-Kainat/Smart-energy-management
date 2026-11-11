class Device:
    """A device inside one building (class Device in our UML diagram)."""

    def __init__(self, device_id, building_id, name, energy_type):
        self._id = device_id
        self._building_id = building_id
        self._name = ""
        self._energy_type = ""

        self.set_name(name)
        self.setup_energy_type(energy_type)   # initialization method

    # ---------- initialization method ----------
    def setup_energy_type(self, energy_type):
        """Check and store the energy type, e.g. 'electricity' or 'gas'."""
        self.set_energy_type(energy_type)

    # ---------- getters ----------
    def get_id(self):
        return self._id

    def get_building_id(self):
        return self._building_id

    def get_name(self):
        return self._name

    def get_energy_type(self):
        return self._energy_type

    # ---------- setters ----------
    # id and building_id have no setter on purpose.
    def set_name(self, name):
        if not name or not name.strip():
            raise ValueError("Device name must not be empty.")
        self._name = name.strip()

    def set_energy_type(self, energy_type):
        if not energy_type or not energy_type.strip():
            raise ValueError("Energy type must not be empty.")
        self._energy_type = energy_type.strip().lower()

    # ---------- method from the UML diagram ----------
    def edit(self, name, energy_type):
        """Change name and energy type together (requirement F8)."""
        self.set_name(name)
        self.set_energy_type(energy_type)

    def __str__(self):
        return f"Device {self._id}: {self._name} ({self._energy_type})"
