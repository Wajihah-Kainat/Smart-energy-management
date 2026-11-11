import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    """A fresh app with an empty temporary database for every test."""
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, name="Anna", email="anna@example.com", password="secret123"):
    return client.post("/register", data={"name": name, "email": email, "password": password})


def make_building(client, name="Main office"):
    client.post("/buildings/add", data={"name": name, "address": "Street 1, Dortmund",
                                        "type": "office", "comfort_temp": "21"})


def make_device(client, building_id=1, name="Heat pump"):
    client.post(f"/buildings/{building_id}/devices", data={"name": name, "energy_type": "electricity"})


@pytest.fixture
def user(client):
    """Logged-in user with 1 building (id 1) and 1 device (id 1)."""
    register(client)
    make_building(client)
    make_device(client)
    return client
