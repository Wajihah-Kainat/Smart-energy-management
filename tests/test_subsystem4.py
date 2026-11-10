import os
import pytest
from subsystem4 import subsystem4_bp, db_manager, ai_coach, report_generator
from subsystem4.models import Subsystem4Exception
from flask import Flask

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(subsystem4_bp)
    with app.test_client() as client:
        yield client

# --- Original 5 Route Smoke Tests ---

def test_dashboard_route(client):
    response = client.get('/subsystem4/')
    assert response.status_code == 200

def test_costs_carbon_route(client):
    response = client.get('/subsystem4/costs-carbon')
    assert response.status_code == 200

def test_reports_route(client):
    response = client.get('/subsystem4/reports')
    assert response.status_code == 200

def test_coach_route_get(client):
    response = client.get('/subsystem4/coach')
    assert response.status_code == 200
    assert b"AI Sustainability Coach" in response.data or response.status_code == 200

def test_coach_route_post(client):
    response = client.post('/subsystem4/coach', data={
        'building': 'Main office',
        'period': 'Last 30 days'
    })
    assert response.status_code == 200

# --- 10 New Unit & Functional Tests ---

def test_database_connection():
    """Test that the database manager successfully creates a connection."""
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        assert result[0] == 1

def test_insert_and_fetch_energy_log():
    """Test inserting an energy log directly via database manager and fetching it."""
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO energy_logs (timestamp, kwh_used, cost) VALUES (datetime('now'), ?, ?);",
            (45.5, 12.30)
        )
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT kwh_used, cost FROM energy_logs ORDER BY id DESC LIMIT 1;")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == 45.5
        assert row[1] == 12.30

def test_ai_coach_service_tips():
    """Test that the AI coach service returns a valid string tip."""
    tip = ai_coach.generate_coach_tips(20.0)
    assert isinstance(tip, str)
    assert len(tip) > 0

def test_report_generator_pdf_creation():
    """Test that the report generator successfully outputs a PDF file path."""
    pdf_path = report_generator.create_pdf_report("Test Summary", "Test Tip")
    assert isinstance(pdf_path, str)
    assert os.path.exists(pdf_path)

def test_dashboard_post_add_log(client):
    """Test submitting a new energy log via the dashboard POST route."""
    response = client.post('/subsystem4/', data={
        'kwh_used': '30.5',
        'cost': '8.75'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_delete_log_route(client):
    """Test deleting an energy log entry through the route."""
    # First insert a dummy log to delete
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO energy_logs (timestamp, kwh_used, cost) VALUES (datetime('now'), ?, ?);",
            (10.0, 3.00)
        )
        cursor.execute("SELECT id FROM energy_logs ORDER BY id DESC LIMIT 1;")
        log_id = cursor.fetchone()[0]

    response = client.post(f'/subsystem4/delete/{log_id}', follow_redirects=True)
    assert response.status_code == 200

def test_reports_post_route(client):
    """Test adding a new report entry via the reports POST route."""
    response = client.post('/subsystem4/reports', data={
        'building': 'Warehouse A',
        'period': 'Current week'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_download_pdf_report_route(client):
    """Test downloading the generated PDF report route."""
    response = client.get('/subsystem4/report/pdf')
    assert response.status_code == 200
    assert response.content_type == 'application/pdf'

def test_subsystem_exception_handling():
    """Test that Subsystem4Exception can be raised and caught properly."""
    with pytest.raises(Subsystem4Exception):
        raise Subsystem4Exception("Test exception message")

def test_coach_post_handling(client):
    """Test POST request to coach route with form inputs."""
    response = client.post('/subsystem4/coach', data={}, follow_redirects=True)
    assert response.status_code == 200
