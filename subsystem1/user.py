from datetime import date


class User:
    """A person who uses the system (class User in our UML diagram)."""

    def __init__(self, user_id, name, email, password_hash):
        # The underscore means: "private". Other code must use the getters and setters.
        self._id = user_id
        self._password_hash = password_hash
        self._name = ""
        self._email = ""
        self._created_at = ""

        self.set_name(name)      # the setters check the values
        self.set_email(email)
        self.setup_account()     # initialization method

    # ---------- initialization method ----------
    def setup_account(self):
        """Set the creation date to today."""
        self._created_at = date.today().isoformat()

    # ---------- getters (read a value) ----------
    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_email(self):
        return self._email

    def get_password_hash(self):
        return self._password_hash

    def get_created_at(self):
        return self._created_at

    # ---------- setters (change a value, with a check) ----------
    # id and created_at have no setter on purpose: they must never change.
    def set_name(self, name):
        if not name or not name.strip():
            raise ValueError("Name must not be empty.")
        self._name = name.strip()

    def set_email(self, email):
        if not email or "@" not in email:
            raise ValueError("Email must contain an @ sign.")
        self._email = email.strip().lower()

    def set_password_hash(self, password_hash):
        if not password_hash:
            raise ValueError("Password hash must not be empty.")
        self._password_hash = password_hash

    # ---------- method from the UML diagram ----------
    def update_profile(self, name, email):
        """Change name and email together (requirement F3)."""
        self.set_name(name)
        self.set_email(email)

    def __str__(self):
        return f"User {self._id}: {self._name} <{self._email}>"
