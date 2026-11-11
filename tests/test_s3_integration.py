# Subsystem 3: cost, carbon, goals and alerts are calculated from the readings of Subsystem 2
from conftest import register, make_building, make_device


def add_reading(client, date, kwh, device_id=1):
    client.post("/readings", data={"device_id": device_id, "date": date, "amount_kwh": kwh})


def configure(client, building_id=1, price=0.5, factor=0.4):
    return client.put(f"/api/v1/s3/settings/{building_id}",
                      json={"price_per_kwh": price, "emission_factor": factor, "factor_source": "test"})


def test_page_needs_login(client):
    assert client.get("/costs-carbon").status_code == 302
    assert client.get("/api/v1/s3/alerts").status_code == 401


def test_page_lists_buildings_of_subsystem_1(user):
    page = user.get("/costs-carbon").get_data(as_text=True)
    assert "Main office" in page and "Save settings" in page


def test_cost_and_carbon_use_the_kwh_from_readings(user):
    add_reading(user, "2026-10-01", 10)
    add_reading(user, "2026-10-02", 20)
    assert configure(user).status_code == 200
    data = user.get("/api/v1/s3/analytics/1?period=month&date=2026-10-15").get_json()
    assert data["energy_kwh"] == 30
    assert data["cost"] == 15.0            # 30 kWh * 0.50
    assert data["carbon_kg"] == 12.0       # 30 kWh * 0.40


def test_analytics_without_settings_gives_clear_error(user):
    response = user.get("/api/v1/s3/analytics/1")
    assert response.status_code == 404 and "not configured" in response.get_json()["error"]


def test_building_must_exist_and_belong_to_user(user, app):
    assert configure(user, building_id=99).status_code == 404
    other = app.test_client()
    register(other, name="Bob", email="bob@example.com")
    assert configure(other, building_id=1).status_code == 404          # Anna's building
    assert other.get("/api/v1/s3/analytics/1").status_code == 404


def test_goal_progress_score_and_alert(user):
    add_reading(user, "2026-10-01", 30)
    configure(user)
    user.put("/api/v1/s3/goals/1", json={"month": "2026-10", "target_kwh": 100, "daily_limit_kwh": 20})
    progress = user.get("/api/v1/s3/goals/1/progress?month=2026-10").get_json()
    assert progress["progress_percent"] == 30.0
    assert 0 <= user.get("/api/v1/s3/score/1?month=2026-10").get_json()["score"] <= 100
    alert = user.post("/api/v1/s3/evaluate-alert/1?date=2026-10-01").get_json()
    assert alert["alert_created"] is True                               # 30 kWh > daily limit 20
    alerts = user.get("/api/v1/s3/alerts?building_id=1").get_json()["alerts"]
    assert len(alerts) == 1
    assert user.patch(f"/api/v1/s3/alerts/{alerts[0]['id']}/read").status_code == 200
    assert user.delete(f"/api/v1/s3/alerts/{alerts[0]['id']}").status_code == 200


def test_invalid_settings_are_rejected(user):
    assert configure(user, price=-1).status_code == 400
    assert user.put("/api/v1/s3/settings/1", json={"price_per_kwh": 1}).status_code == 400


def test_page_shows_saved_settings(user):
    configure(user, price=0.42)
    assert 'value="0.42"' in user.get("/costs-carbon").get_data(as_text=True)
