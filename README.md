# AI-Powered Smart Energy Management System

## Team Members & Roles
- **Arshia Fatima** — Subsystem 1: User & Building Management
- **Melika Soheilifar** — Subsystem 2: Energy Monitoring & Dashboard
- **Wajihah Kainat** — Subsystem 3: Cost, Savings, Carbon & Score
- **Faryal Mahmood** — Subsystem 4: AI Sustainability Coach & Reports

## Technology Stack
Python, Flask, SQLite, HTML/CSS, Chart.js, OpenAI API, pytest, Docker.

## Subsystem 4: AI Sustainability Coach & Reports

### Installation & Test Commands
```bash
python -m pip install -r requirements.txt
PYTHONPATH=. python3 -m pytest -v
```

### UML Diagram
<img width="1381" height="718" alt="WhatsApp Image 2026-11-07 at 18 29 11" src="https://github.com/user-attachments/assets/cf4395cb-880b-450c-9393-0950ca5dd39d" />

Implemented OOP Classes (Subsystem 4)

All classes are in subsystem4/models.py. Each class has a constructor, initialization/configuration logic, getters and setters, and validation where appropriate.

AICoachEngine: processes building type and time period inputs for generative or rule-based recommendations.
ReportGenerator: structures aggregated SQLite energy metrics and PDF layout generation.
EnergyDataConnector: manages local telemetry lookup and persistence for Subsystem 4.
CoachPromptBuilder: formats customized prompt contexts based on building utilization metrics.
ReportTemplateManager: validates template rendering and file assets.

Architecture

models.py: OOP domain model, AI recommendation logic, and reporting structure.
app.py: Flask Blueprint routes, dashboard views, and PDF download endpoints (subsystem4_bp).
templates/: web dashboard, coach interface, and report templates.
tests/: unit and integration test suites (test_subsystem4.py).

Error Handling Approach

This project follows the Python exception model from the official tutorial: raise explicit exceptions for invalid input, lookup misses, and template failures, then translate them into consistent HTTP responses in the Flask blueprint. Each domain area (coaching, reporting, and dashboard rendering) has a dedicated custom exception type to make failures easier to diagnose and test.

The class model is intentionally separate from Flask so it can be tested without running the web server.

Formulas and Assumptions

AI recommendation heuristics select targeted conservation advice matching specific building profiles (e.g., HVAC scheduling, envelope insulation, LED retrofits).
PDF generation packages aggregated SQLite energy metrics into a formatted document output stream (sustainability_report.pdf).
Parameter validation checks form payloads for the coach endpoint to prevent empty inputs or invalid period selections.
The coach advice and generated reports are configured for demonstration and project evaluation purposes.

Run Locally (Windows PowerShell)

python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
Open http://127.0.0.1:5000.

To add demo data, in another terminal run:

.venv\Scripts\Activate.ps1
python seed_demo.py
Demo data uses owner ID 1, building ID 1.

Run Tests

PYTHONPATH=. python3 -m pytest -v
Tests use a temporary SQLite database. Run them locally to obtain actual test results; this repository does not claim tests passed unless you run the command and see the result.

Docker

docker compose up --build
Open http://127.0.0.1:5000. The SQLite database is stored in the data volume.

API Overview

The standalone demo uses X-User-ID to simulate the authenticated user. This is a development-only adapter, not production authentication. During integration, replace it with the logged-in identity from Subsystem 1 and verify ownership on every request.

GET /dashboard
GET /costs-carbon
GET /reports
GET /reports/download
GET /coach
POST /coach

GitHub faryal Branch Workflow

From the project directory, connect your GitHub repository as origin first, then run:

git init
git switch -c faryal
git add .
git commit -m "Finalize Subsystem 4 implementation, templates, and passing test suite"
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin faryal

If your repository already exists and has a remote, do not repeat git init or git remote add origin. Create/switch to the branch and push it.

Project Structure & Component List

app.py: Root application entry point for the Flask server.
subsystem4/:
  __init__.py: Blueprint and route handlers for Subsystem 4.
  models.py: Core logic classes (DatabaseManager, AICoachService, ReportGenerator).
  templates/: HTML templates (dashboard.html, coach.html, reports.html, costs_carbon.html).
requirements.txt: Project Python package dependencies.

Team Video Presentation

Add the real video URL here after the team records and uploads the 3–5 minute presentation:

Presentation: https://drive.google.com/drive/folders/1uDiISZIS1JcYvcanFNMtXTVZVyKt_kZe?usp=drive_link

Before Submission Checklist
Before Submission Checklist

- [x] Root-level `app.py` created for Flask blueprint registration[span_0](start_span)[span_0](end_span)[span_1](start_span)[span_1](end_span)
- [x] Subsystem 4 `__init__.py` template rendering updated from `index.html` to `dashboard.html`[span_2](start_span)[span_2](end_span)
- [x] `requirements.txt` standardized to include core dependencies (`flask`, `reportlab`, `openai`, `pytest`)[span_3](start_span)[span_3](end_span)
- [x] 15 comprehensive unit and functional tests written and integrated[span_4](start_span)[span_4](end_span)
- [x] `README.md` cleaned up to list only existing components and files[span_5](start_span)[span_5](end_span)
- [x] All changes committed and pushed to the `faryal` branch[span_6](start_span)[span_6](end_span)

