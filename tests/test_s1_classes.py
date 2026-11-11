# Unit tests for the S1 classes User, Building and Device (run with:  python -m pytest)
import pytest

from app import create_app
from app.db import get_db
from app.s1 import Building, Device, User


@pytest.fixture
def db(tmp_path):
    """A fresh temporary database; the classes write into it."""
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    with app.app_context():
        yield get_db()


# ----------------------------------------------------------------- User
def test_user_check_registration():
    assert User.check_registration("Anna", "anna@example.com", "secret123") is None
    assert User.check_registration("", "anna@example.com", "secret123") is not None
    assert User.check_registration("Anna", "no-email", "secret123") is not None
    assert User.check_registration("Anna", "anna@example.com", "short") is not None


def test_user_create_hashes_the_password():
    user = User.create("Anna", "anna@example.com", "secret123")
    assert user.password_hash != "secret123"
    assert user.password_matches("secret123")
    assert not user.password_matches("wrong-password")


def test_user_insert_and_find_by_email(db):
    user = User.create("Anna", "anna@example.com", "secret123")
    user_id = user.insert(db)
    found = User.find_by_email(db, "anna@example.com")
    assert found.id == user_id and found.name == "Anna"
    assert User.find_by_email(db, "nobody@example.com") is None


# ------------------------------------------------------------- Building
def test_building_check_uses_default_comfort_temperature():
    assert Building.check("Tower", "Street 1", "office", "") == (None, 21.0)
    assert Building.check("Tower", "Street 1", "office", "22,5") == (None, 22.5)


@pytest.mark.parametrize("bad", [("", "Street 1", "office", ""),
                                 ("Tower", "", "office", ""),
                                 ("Tower", "Street 1", "castle", ""),
                                 ("Tower", "Street 1", "office", "abc"),
                                 ("Tower", "Street 1", "office", "35")])
def test_building_check_rejects_bad_input(bad):
    error, temp = Building.check(*bad)
    assert error is not None and temp is None


def test_building_insert_update_delete(db):
    user_id = User.create("Anna", "anna@example.com", "secret123").insert(db)
    building = Building(user_id, "Tower", "Street 1", "office")
    building_id = building.insert(db)
    Device(building_id, "Heat pump", "electricity").insert(db)

    building.name = "New tower"
    building.update(db)
    row = db.execute("SELECT * FROM buildings WHERE id = ?", (building_id,)).fetchone()
    assert row["name"] == "New tower" and row["comfort_temp"] == 21.0

    Building.delete(db, building_id)
    assert db.execute("SELECT COUNT(*) FROM buildings").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM devices").fetchone()[0] == 0


# --------------------------------------------------------------- Device
def test_device_check():
    assert Device.check("Heat pump", "electricity") is None
    assert Device.check("", "electricity") is not None
    assert Device.check("Heat pump", "coal") is not None


def test_device_insert_update_delete(db):
    user_id = User.create("Anna", "anna@example.com", "secret123").insert(db)
    building_id = Building(user_id, "Tower", "Street 1", "office").insert(db)
    device = Device(building_id, "Heat pump", "electricity")
    device_id = device.insert(db)

    device.energy_type = "gas"
    device.update(db)
    row = db.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
    assert row["energy_type"] == "gas"

    Device.delete(db, device_id)
    assert db.execute("SELECT COUNT(*) FROM devices").fetchone()[0] == 0
