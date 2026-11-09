# Tests for Subsystem 1 (run with:  python -m pytest)
import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    """A fresh app with an empty temporary database for every test."""
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


def register(client, name="Anna", email="anna@example.com", password="secret123"):
    return client.post("/register", data={"name": name, "email": email, "password": password})


def login(client, email="anna@example.com", password="secret123"):
    return client.post("/login", data={"email": email, "password": password})


def add_building(client, **changes):
    data = {"name": "Test Tower", "address": "Street 1, Dortmund",
            "type": "office", "comfort_temp": "21"}
    data.update(changes)
    return client.post("/buildings/add", data=data)


# ---------------------------------------------------------------- users
def test_register_and_see_buildings_page(client):
    response = register(client)
    assert response.status_code == 302
    assert client.get("/buildings").status_code == 200


def test_password_is_stored_as_hash(client):
    register(client)
    import sqlite3
    row = sqlite3.connect(client.application.config["DATABASE"]).execute(
        "SELECT password_hash FROM users").fetchone()
    assert row[0] != "secret123"
    assert row[0].startswith(("scrypt:", "pbkdf2:"))


def test_same_email_twice_is_not_allowed(client):
    register(client)
    response = register(client, name="Other", email="ANNA@example.com")   # upper case too
    assert response.status_code == 400
    assert b"already registered" in response.data


def test_bad_email_is_rejected(client):
    assert register(client, email="not-an-email").status_code == 400


def test_short_password_is_rejected(client):
    response = register(client, password="short")
    assert response.status_code == 400
    assert b"at least 8" in response.data


def test_login_and_logout(client):
    register(client)
    client.post("/logout")
    assert login(client).status_code == 302
    assert client.get("/buildings").status_code == 200
    client.post("/logout")
    assert client.get("/buildings").status_code == 302       # sent to the login page


def test_wrong_password_is_rejected(client):
    register(client)
    client.post("/logout")
    assert login(client, password="wrong-password").status_code == 401


def test_buildings_need_login(client):
    response = client.get("/buildings")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


# ------------------------------------------------------------- buildings
def test_add_building_and_see_it_in_list(client):
    register(client)
    assert add_building(client).status_code == 302
    page = client.get("/buildings").data
    assert b"Test Tower" in page and b"Dortmund" in page


def test_empty_comfort_temperature_uses_default_21(client):
    register(client)
    add_building(client, comfort_temp="")
    assert b"21 \xc2\xb0C" in client.get("/buildings").data


@pytest.mark.parametrize("bad", ["5", "35", "warm"])
def test_bad_comfort_temperature_is_rejected(client, bad):
    register(client)
    assert add_building(client, comfort_temp=bad).status_code == 400


def test_bad_building_type_is_rejected(client):
    register(client)
    assert add_building(client, type="castle").status_code == 400


def test_edit_building(client):
    register(client)
    add_building(client)
    client.post("/buildings/1/edit", data={"name": "New name", "address": "Road 2",
                                           "type": "home", "comfort_temp": "22"})
    assert b"New name" in client.get("/buildings").data


def test_delete_building_also_deletes_its_devices(client):
    register(client)
    add_building(client)
    client.post("/buildings/1/devices", data={"name": "Pump A", "energy_type": "electricity"})
    client.post("/buildings/1/delete")
    assert b"Test Tower" not in client.get("/buildings").data
    import sqlite3
    count = sqlite3.connect(client.application.config["DATABASE"]).execute(
        "SELECT COUNT(*) FROM devices").fetchone()[0]
    assert count == 0


# ---------------------------------------------------- rule: only your own data
def test_other_user_cannot_see_or_change_my_building(client):
    register(client)
    add_building(client)
    client.post("/logout")
    register(client, name="Ben", email="ben@example.com")
    assert client.get("/buildings/1").status_code == 404
    assert client.post("/buildings/1/delete").status_code == 404
    assert client.post("/buildings/1/devices",
                       data={"name": "X", "energy_type": "gas"}).status_code == 404
    assert b"Test Tower" not in client.get("/buildings").data


# ---------------------------------------------------------------- devices
def test_add_edit_delete_device(client):
    register(client)
    add_building(client)
    client.post("/buildings/1/devices", data={"name": "Pump A", "energy_type": "electricity"})
    assert b"Pump A" in client.get("/buildings/1").data
    client.post("/devices/1/edit", data={"name": "Boiler B", "energy_type": "gas"})
    page = client.get("/buildings/1").data
    assert b"Boiler B" in page and b"Pump A" not in page
    client.post("/devices/1/delete")
    assert b"Boiler B" not in client.get("/buildings/1").data


def test_bad_device_is_rejected(client):
    register(client)
    add_building(client)
    assert client.post("/buildings/1/devices",
                       data={"name": "", "energy_type": "gas"}).status_code == 400
    assert client.post("/buildings/1/devices",
                       data={"name": "Lamp", "energy_type": "magic"}).status_code == 400
