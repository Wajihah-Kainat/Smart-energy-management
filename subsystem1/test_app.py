import pytest
from subsystem1.app import create_app


@pytest.fixture
def client():
    """A fresh app (and empty data) for every test."""
    app = create_app()
    app.testing = True
    return app.test_client()


def register(client, email="a@b.com", name="Arshia", password="secret123"):
    return client.post("/register", json={"name": name, "email": email, "password": password})


def add_building(client, user_id=1, building_type="office", **extra):
    data = {"user_id": user_id, "name": "Main", "address": "Street 1", "type": building_type}
    data.update(extra)
    return client.post("/buildings", json=data)


def test_register_works(client):
    response = register(client)
    assert response.status_code == 201
    assert response.get_json()["email"] == "a@b.com"


def test_register_never_returns_password(client):
    assert "password" not in str(register(client).get_json()).lower()


def test_register_duplicate_email_gives_409(client):
    register(client)
    response = register(client, email="A@B.com")
    assert response.status_code == 409
    assert "already registered" in response.get_json()["error"]


def test_register_bad_email_gives_400(client):
    assert register(client, email="no-at-sign").status_code == 400


def test_register_without_password_gives_400(client):
    assert register(client, password="").status_code == 400


def test_add_building_works_with_default_temp(client):
    register(client)
    response = add_building(client)
    assert response.status_code == 201
    assert response.get_json()["comfort_temp"] == 21.0


def test_add_building_unknown_user_gives_404(client):
    assert add_building(client, user_id=99).status_code == 404


def test_add_building_bad_type_gives_400(client):
    register(client)
    assert add_building(client, building_type="castle").status_code == 400


def test_add_building_wrong_temp_type_gives_400(client):
    register(client)
    assert add_building(client, comfort_temp="hot").status_code == 400


def test_list_shows_only_own_buildings(client):
    register(client)
    register(client, email="other@b.com")
    add_building(client, user_id=1)
    add_building(client, user_id=2)
    response = client.get("/buildings?user_id=1")
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_owner_can_read_own_building(client):
    register(client)
    add_building(client)
    assert client.get("/buildings/1?user_id=1").status_code == 200


def test_other_user_gets_403(client):
    register(client)
    register(client, email="other@b.com")
    add_building(client, user_id=1)
    assert client.get("/buildings/1?user_id=2").status_code == 403


def test_unknown_building_gives_404(client):
    register(client)
    assert client.get("/buildings/5?user_id=1").status_code == 404


def test_failed_registration_does_not_use_up_an_id(client):
    register(client, email="no-at-sign")                 # fails
    assert register(client).get_json()["id"] == 1        # first real user still gets id 1
