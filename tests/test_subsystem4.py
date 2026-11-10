import pytest
from subsystem4.app import subsystem4_bp
from flask import Flask

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(subsystem4_bp)
    with app.test_client() as client:
        yield client

def test_dashboard_route(client):
    response = client.get('/dashboard')
    assert response.status_code == 200

def test_costs_carbon_route(client):
    response = client.get('/costs-carbon')
    assert response.status_code == 200

def test_reports_route(client):
    response = client.get('/reports')
    assert response.status_code == 200

def test_coach_route_get(client):
    response = client.get('/coach')
    assert response.status_code == 200
    assert b"AI Sustainability Coach" in response.data

def test_coach_route_post(client):
    response = client.post('/coach', data={
        'building': 'Main office',
        'period': 'Last 30 days'
    })
    assert response.status_code == 200
    assert b"Your tips" in response.data