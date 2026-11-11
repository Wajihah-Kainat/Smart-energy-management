
import pytest

from app import create_app
from database import init_db
from models.energy_reading import (
    add_reading,
    update_reading,
    delete_reading,
)


@pytest.fixture
def database(tmp_path):
    """Create an isolated test database."""
    db_path = str(tmp_path / "test_energy.db")
    init_db(db_path)
    return db_path


@pytest.fixture
def app(database):
    """Create a Flask application for testing."""
    app = create_app()

    app.config.update({
        "TESTING": True,
        "DATABASE": database,
    })

    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_add_reading(database):
    reading_id = add_reading(
        device_id=1,
        reading_date="2026-11-03",
        amount_kwh=5.5,
        database=database,
    )

    assert reading_id is not None


def test_reject_negative_energy(database):
    with pytest.raises(ValueError):
        add_reading(
            device_id=1,
            reading_date="2026-11-03",
            amount_kwh=-3,
            database=database,
        )


def test_reject_invalid_date(database):
    with pytest.raises(ValueError):
        add_reading(
            device_id=1,
            reading_date="03-11-2026",
            amount_kwh=3.2,
            database=database,
        )


def test_update_reading(database):
    reading_id = add_reading(
        device_id=1,
        reading_date="2026-11-03",
        amount_kwh=4.0,
        database=database,
    )

    result = update_reading(
        reading_id=reading_id,
        device_id=1,
        reading_date="2026-11-03",
        amount_kwh=7.5,
        database=database,
    )

    assert result is True


def test_delete_reading(database):
    reading_id = add_reading(
        device_id=1,
        reading_date="2026-11-03",
        amount_kwh=2.5,
        database=database,
    )

    result = delete_reading(
        reading_id,
        database=database,
    )

    assert result is True


def test_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200


def test_readings_page_loads(client):
    response = client.get("/readings")
    assert response.status_code == 200


def test_csv_export(client):
    response = client.get("/readings/export")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"


def test_live_simulation(client):
    response = client.post(
        "/readings/simulate",
        json={"device_id": 1}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["reading"]["type"] == "Simulated"
