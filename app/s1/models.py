# Subsystem 1: classes User, Building and Device.
# Each class keeps its data, checks it and writes it to the database.
import re
from datetime import date

from werkzeug.security import check_password_hash, generate_password_hash

BUILDING_TYPES = ("office", "university", "home")
ENERGY_TYPES = ("electricity", "gas", "solar")
DEFAULT_COMFORT_TEMP = 21.0
MIN_PASSWORD_LENGTH = 8
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ------------------------------------------------------------------- the classes
class User:
    """A person who can log in. Stored in the table users."""

    def __init__(self, name, email, password_hash, created_at=None, id=None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash          # never the plain password
        self.created_at = created_at

    @staticmethod
    def check_registration(name, email, password):
        """Return an error message, or None if everything is fine."""
        if not name:
            return "Please enter your name."
        if not EMAIL_PATTERN.match(email):
            return "Please enter a valid email address."
        if len(password) < MIN_PASSWORD_LENGTH:
            return f"The password must have at least {MIN_PASSWORD_LENGTH} characters."
        return None

    @classmethod
    def create(cls, name, email, password):
        """A new user: the password is turned into a hash right here."""
        return cls(name, email, generate_password_hash(password),
                   date.today().isoformat())

    def password_matches(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def find_by_email(cls, db, email):
        row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row is None:
            return None
        return cls(row["name"], row["email"], row["password_hash"],
                   row["created_at"], row["id"])

    def insert(self, db):
        cursor = db.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (self.name, self.email, self.password_hash, self.created_at))
        db.commit()
        self.id = cursor.lastrowid
        return self.id


class Building:
    """A building of one user. Stored in the table buildings."""

    def __init__(self, user_id, name, address, building_type,
                 comfort_temp=DEFAULT_COMFORT_TEMP, id=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.address = address
        self.type = building_type
        self.comfort_temp = comfort_temp

    @staticmethod
    def check(name, address, building_type, comfort_text):
        """Return (error, comfort_temp). comfort_temp is a number when there is no error."""
        if not name:
            return "Please enter a building name.", None
        if not address:
            return "Please enter an address.", None
        if building_type not in BUILDING_TYPES:
            return "The type must be office, university or home.", None
        if comfort_text == "":
            return None, DEFAULT_COMFORT_TEMP          # empty -> default 21
        try:
            comfort_temp = float(comfort_text.replace(",", "."))
        except ValueError:
            return "The comfort temperature must be a number.", None
        if not 10 <= comfort_temp <= 30:
            return "The comfort temperature must be between 10 and 30 °C.", None
        return None, comfort_temp

    def insert(self, db):
        cursor = db.execute(
            "INSERT INTO buildings (user_id, name, address, type, comfort_temp) "
            "VALUES (?, ?, ?, ?, ?)",
            (self.user_id, self.name, self.address, self.type, self.comfort_temp))
        db.commit()
        self.id = cursor.lastrowid
        return self.id

    def update(self, db):
        db.execute(
            "UPDATE buildings SET name = ?, address = ?, type = ?, comfort_temp = ? "
            "WHERE id = ?",
            (self.name, self.address, self.type, self.comfort_temp, self.id))
        db.commit()

    @staticmethod
    def delete(db, building_id):
        """Delete a building and its devices (readings etc. follow by cascade)."""
        db.execute("DELETE FROM devices WHERE building_id = ?", (building_id,))
        db.execute("DELETE FROM buildings WHERE id = ?", (building_id,))
        db.commit()


class Device:
    """An energy device of one building. Stored in the table devices."""

    def __init__(self, building_id, name, energy_type, id=None):
        self.id = id
        self.building_id = building_id
        self.name = name
        self.energy_type = energy_type

    @staticmethod
    def check(name, energy_type):
        """Return an error message, or None if everything is fine."""
        if not name:
            return "Please enter a device name."
        if energy_type not in ENERGY_TYPES:
            return "The energy type must be electricity, gas or solar."
        return None

    def insert(self, db):
        cursor = db.execute(
            "INSERT INTO devices (building_id, name, energy_type) VALUES (?, ?, ?)",
            (self.building_id, self.name, self.energy_type))
        db.commit()
        self.id = cursor.lastrowid
        return self.id

    def update(self, db):
        db.execute("UPDATE devices SET name = ?, energy_type = ? WHERE id = ?",
                   (self.name, self.energy_type, self.id))
        db.commit()

    @staticmethod
    def delete(db, device_id):
        db.execute("DELETE FROM devices WHERE id = ?", (device_id,))
        db.commit()
