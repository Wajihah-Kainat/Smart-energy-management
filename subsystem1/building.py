class Building:
    """A building owned by one user (class Building in our UML diagram)."""

    VALID_TYPES = ("office", "university", "home")
    DEFAULT_COMFORT_TEMP = 21.0

    def __init__(self, building_id, user_id, name, address, building_type, comfort_temp=None):
        self._id = building_id
        self._user_id = user_id
        self._name = ""
        self._address = ""
        self._type = ""
        self._comfort_temp = None
        self._devices = []       # the devices inside this building (Building 1 - * Device)

        self.set_name(name)
        self.set_address(address)
        self.set_type(building_type)
        self.set_comfort_temp(comfort_temp)
        self.apply_defaults()    # initialization method

    # ---------- initialization method ----------
    def apply_defaults(self):
        """If the user gave no comfort temperature, use the default."""
        if self._comfort_temp is None:
            self._comfort_temp = self.DEFAULT_COMFORT_TEMP

    # ---------- getters ----------
    def get_id(self):
        return self._id

    def get_user_id(self):
        return self._user_id

    def get_name(self):
        return self._name

    def get_address(self):
        return self._address

    def get_type(self):
        return self._type

    def get_comfort_temp(self):
        return self._comfort_temp

    def get_devices(self):
        return list(self._devices)   # a copy, so nobody changes our list by accident

    # ---------- setters ----------
    # id and user_id have no setter: a building never changes its owner.
    def set_name(self, name):
        if not name or not name.strip():
            raise ValueError("Building name must not be empty.")
        self._name = name.strip()

    def set_address(self, address):
        if not address or not address.strip():
            raise ValueError("Address must not be empty.")
        self._address = address.strip()

    def set_type(self, building_type):
        if building_type not in self.VALID_TYPES:
            raise ValueError(f"Type must be one of {self.VALID_TYPES}.")
        self._type = building_type

    def set_comfort_temp(self, comfort_temp):
        # None is allowed here: apply_defaults() fills it in.
        if comfort_temp is not None and not 10 <= comfort_temp <= 30:
            raise ValueError("Comfort temperature must be between 10 and 30 degrees.")
        self._comfort_temp = comfort_temp

    # ---------- methods ----------
    def edit(self, name, address, building_type, comfort_temp):
        """Change all editable values together (requirements F5, F6)."""
        self.set_name(name)
        self.set_address(address)
        self.set_type(building_type)
        self.set_comfort_temp(comfort_temp)
        self.apply_defaults()

    def add_device(self, device):
        """Put a device into this building (requirement F7)."""
        if device.get_building_id() != self._id:
            raise ValueError("This device belongs to another building.")
        self._devices.append(device)

    def __str__(self):
        return f"Building {self._id}: {self._name} ({self._type}), comfort {self._comfort_temp} C"
