# The whole project as one website: S1 -> S2 -> S3 -> S4 with one login and one database
from conftest import register


def test_every_page_is_protected_by_the_login_of_subsystem_1(client):
    for url in ("/dashboard", "/readings", "/costs-carbon", "/coach", "/reports", "/buildings"):
        response = client.get(url)
        assert response.status_code == 302 and "/login" in response.headers["Location"], url


def test_navigation_links_all_pages(user):
    page = user.get("/dashboard").get_data(as_text=True)
    for link in ("/buildings", "/dashboard", "/readings", "/costs-carbon", "/coach", "/reports"):
        assert f'href="{link}"' in page


def test_full_flow_from_building_to_report(client):
    register(client)
    client.post("/buildings/add", data={"name": "Lab", "address": "A 1", "type": "university", "comfort_temp": "20"})
    client.post("/buildings/1/devices", data={"name": "Oven", "energy_type": "electricity"})
    client.post("/readings", data={"device_id": 1, "date": "2026-10-03", "amount_kwh": "40"})
    client.put("/api/v1/s3/settings/1", json={"price_per_kwh": 0.25, "emission_factor": 0.5, "factor_source": "t"})
    client.put("/api/v1/s3/goals/1", json={"month": "2026-10", "target_kwh": 80, "daily_limit_kwh": 30})
    analytics = client.get("/api/v1/s3/analytics/1?date=2026-10-01").get_json()
    assert (analytics["energy_kwh"], analytics["cost"], analytics["carbon_kg"]) == (40, 10.0, 20.0)
    client.post("/reports", data={"building_id": 1, "period": "2026-10"})
    page = client.get("/reports").get_data(as_text=True)
    assert "Lab" in page and "40.0 kWh" in page and "€10.00" in page and "20.00 kg" in page


def test_users_cannot_see_each_others_data(user, app):
    user.post("/readings", data={"device_id": 1, "date": "2026-10-03", "amount_kwh": "9"})
    other = app.test_client()
    register(other, name="Bob", email="bob@example.com")
    assert "Main office" not in other.get("/readings").get_data(as_text=True)
    assert other.post("/readings", data={"device_id": 1, "date": "2026-10-03", "amount_kwh": "5"}).status_code == 302
    assert other.get("/readings/export").get_data(as_text=True).count("\n") == 1      # header only
    assert other.post("/readings/delete/1").status_code == 302
    assert "9.0" in user.get("/readings").get_data(as_text=True)                      # still there
    assert "Reading does not exist" in other.get("/readings/edit/1", follow_redirects=True).get_data(as_text=True)


def test_login_page_and_logout_still_work(client):
    assert client.get("/login").status_code == 200
    register(client)
    client.post("/logout")
    assert client.get("/dashboard").status_code == 302
