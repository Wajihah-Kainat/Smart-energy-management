# Subsystem 2: readings are linked to the devices of Subsystem 1
import sqlite3

from conftest import make_building, make_device, register
from app.s2.models.energy_reading import add_reading, delete_reading, list_readings, update_reading
from app.s2.services.statistics import Statistics
import pytest


def add(client, device_id=1, date="2026-10-05", kwh="12.5"):
    return client.post("/readings", data={"device_id": device_id, "date": date, "amount_kwh": kwh})


def test_devices_in_the_form_come_from_subsystem_1(user):
    page = user.get("/readings").get_data(as_text=True)
    assert "Main office – Heat pump" in page


def test_no_devices_message_without_s1_data(client):
    register(client)
    assert "No devices yet" in client.get("/readings").get_data(as_text=True)


def test_add_edit_delete_reading(user, app):
    add(user)
    assert "12.5" in user.get("/readings").get_data(as_text=True)
    user.post("/readings/edit/1", data={"device_id": 1, "date": "2026-10-06", "amount_kwh": "8"})
    page = user.get("/readings").get_data(as_text=True)
    assert "2026-10-06" in page and "8.0" in page
    user.post("/readings/delete/1")
    assert "No readings available yet" in user.get("/readings").get_data(as_text=True)


@pytest.mark.parametrize("date,kwh", [("2026-13-40", "5"), ("2026-10-05", "-3"), ("2026-10-05", "0"), ("2026-10-05", "abc")])
def test_invalid_reading_is_rejected(user, date, kwh):
    add(user, date=date, kwh=kwh)
    assert "No readings available yet" in user.get("/readings").get_data(as_text=True)


def test_reading_for_unknown_device_is_rejected(user):
    add(user, device_id=99)
    assert "No readings available yet" in user.get("/readings").get_data(as_text=True)


def test_filter_and_csv_export(user):
    add(user, date="2026-10-01", kwh="1")
    add(user, date="2026-10-20", kwh="2")
    page = user.get("/readings?date_from=2026-10-10").get_data(as_text=True)
    assert "2026-10-20" in page and "2026-10-01" not in page
    csv_text = user.get("/readings/export").get_data(as_text=True)
    assert "Main office,Heat pump,2026-10-01,1.0,Real" in csv_text


def test_live_simulation_creates_simulated_reading(user):
    result = user.post("/readings/simulate", json={"device_id": 1}).get_json()
    assert result["success"] and result["reading"]["type"] == "Simulated"
    assert user.post("/readings/simulate", json={"device_id": 99}).status_code == 400


def test_dashboard_numbers_come_from_readings_and_devices(user):
    add(user, date="2026-10-01", kwh="10")
    add(user, date="2026-10-02", kwh="5")
    make_device(user, name="Lighting")
    page = user.get("/dashboard").get_data(as_text=True)
    assert "15.0 kWh" in page            # total from readings
    assert "<strong>2</strong>" in page  # 2 devices registered in S1 (was hard-coded 3 before)


def test_statistics_class_filters_by_user_and_building(user, app):
    add(user, kwh="4")
    with app.app_context():
        assert Statistics(user_id=1).total_consumption() == 4.0
        assert Statistics(user_id=2).total_consumption() == 0
        assert Statistics(user_id=1, building_id=99).reading_count() == 0


def test_deleting_a_device_or_building_removes_its_readings(user, app):
    add(user)
    user.post("/devices/1/delete")
    with app.app_context():
        assert list_readings(user_id=1) == []
    make_device(user, name="Again")
    add(user, device_id=2)
    user.post("/buildings/1/delete")
    count = sqlite3.connect(app.config["DATABASE"]).execute("SELECT COUNT(*) FROM energy_reading").fetchone()[0]
    assert count == 0


def test_model_functions_validate_input(user, app):
    with app.app_context():
        with pytest.raises(ValueError):
            add_reading(0, "2026-10-01", 5)
        with pytest.raises(ValueError):
            update_reading(1, 1, "2026-10-01", 5, user_id=1)      # reading does not exist
        with pytest.raises(ValueError):
            delete_reading(-1)
