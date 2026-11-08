def setup_data(client):
    assert client.put("/api/v1/s3/settings/1", json={
        "price_per_kwh": 0.30, "emission_factor": 0.4, "factor_source": "Test factor"
    }).status_code == 200
    assert client.put("/api/v1/s3/goals/1", json={
        "target_kwh": 100, "month": "2026-10", "daily_limit_kwh": 10
    }).status_code == 200

def test_health(client):
    assert client.get("/health").json["status"] == "ok"

def test_analytics_and_score(client):
    setup_data(client)
    r = client.post("/api/v1/s3/readings", json={
        "building_id": 1, "reading_date": "2026-10-28", "amount_kwh": 20
    })
    assert r.status_code == 201
    result = client.get("/api/v1/s3/analytics/1?period=month&date=2026-10-28").json
    assert result["energy_kwh"] == 20
    assert result["cost"] == 6
    assert result["carbon_kg"] == 8
    assert "score" in client.get("/api/v1/s3/score/1?month=2026-10").json

def test_goal_progress_and_alert_lifecycle(client):
    setup_data(client)
    client.post("/api/v1/s3/readings", json={
        "building_id": 1, "reading_date": "2026-10-28", "amount_kwh": 12
    })
    progress = client.get("/api/v1/s3/goals/1/progress?month=2026-10").json
    assert progress["progress_percent"] == 12
    evaluated = client.post("/api/v1/s3/evaluate-alert/1?date=2026-10-28").json
    assert evaluated["alert_created"] is True
    alerts = client.get("/api/v1/s3/alerts?building_id=1").json["alerts"]
    assert len(alerts) == 1
    alert_id = alerts[0]["id"]
    assert client.patch(f"/api/v1/s3/alerts/{alert_id}/read").status_code == 200
    assert client.delete(f"/api/v1/s3/alerts/{alert_id}").status_code == 200

def test_invalid_input_is_reported(client):
    response = client.put("/api/v1/s3/settings/1", json={
        "price_per_kwh": -1, "emission_factor": 0.4, "factor_source": "Test"
    })
    assert response.status_code == 400
    assert "price_per_kwh" in response.json["error"]

def test_alerts_are_scoped_to_owner(client):
    setup_data(client)
    client.post("/api/v1/s3/readings", headers={"X-User-ID":"1"}, json={
        "building_id": 1, "reading_date": "2026-10-28", "amount_kwh": 12
    })
    client.post("/api/v1/s3/evaluate-alert/1?date=2026-10-28", headers={"X-User-ID":"1"})
    own = client.get("/api/v1/s3/alerts?building_id=1", headers={"X-User-ID":"1"}).json["alerts"]
    other = client.get("/api/v1/s3/alerts?building_id=1", headers={"X-User-ID":"2"}).json["alerts"]
    assert len(own) == 1
    assert len(other) == 0


def test_invalid_user_header_returns_403(client):
    response = client.get("/api/v1/s3/analytics/1", headers={"X-User-ID": "0"})
    assert response.status_code == 403
    assert "positive integer" in response.json["error"]


def test_invalid_json_payload_returns_400(client):
    response = client.put("/api/v1/s3/settings/1", data="not-json", content_type="application/json")
    assert response.status_code == 400
    assert "JSON object" in response.json["error"]


def test_missing_goal_returns_404(client):
    response = client.get("/api/v1/s3/goals/1/progress?month=2026-11")
    assert response.status_code == 404
    assert "No goal" in response.json["error"]


def test_missing_alert_returns_404(client):
    response = client.patch("/api/v1/s3/alerts/999/read")
    assert response.status_code == 404
    assert "Alert not found" in response.json["error"]


def test_invalid_period_returns_400(client):
    setup_data(client)
    response = client.get("/api/v1/s3/analytics/1?period=year&date=2026-10-28")
    assert response.status_code == 400
    assert "period" in response.json["error"]
