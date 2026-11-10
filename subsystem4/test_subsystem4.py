import os
import pytest
from flask import Flask
from subsystem4.app import subsystem4_bp
from subsystem4.models import DatabaseManager, AICoachService, ReportGenerator, Subsystem4Exception

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(subsystem4_bp)
    
    with app.test_client() as client:
        yield client

def test_coach_route_get(client):
    """Test that the /coach page loads successfully (GET)."""
    response = client.get('/subsystem4/coach')
    assert response.status_code == 200
    assert b"AI Sustainability Coach" in response.data

def test_coach_route_post(client):
    """Test submitting the coach form to generate AI tips (POST)."""
    response = client.post('/subsystem4/coach', data={
        'building': 'Main office',
        'period': 'Last 30 days'
    })
    assert response.status_code == 200
    assert b"Your AI Tips" in response.data

def test_reports_route_get(client):
    """Test that the /reports page loads successfully (GET)."""
    response = client.get('/subsystem4/reports')
    assert response.status_code == 200
    assert b"Reports" in response.data

def test_pdf_download_route(client):
    """Test downloading the PDF report."""
    response = client.get('/subsystem4/report/pdf')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'