# Smart Energy Management System — Subsystem 3 (OOP Assignment)

**Subsystem:** Cost, Savings, Carbon & Sustainability Score  
**Stack:** Python 3.11+, Flask, SQLite, pytest, HTML/CSS/JavaScript, Docker

This version refactors Subsystem 3 into explicit object-oriented domain classes to match the Homeassignment1 OOP requirements while retaining a small runnable Flask application.

## Team overview

| Team member | Assigned subsystem |
|---|---|
| Arshia Fatima | S1 — User & Building Management |
| Melika Soheyli | S2 — Energy Monitoring & Dashboard |
| Wajihah Kainat | S3 — Cost, Savings, Carbon & Score |
| Faryal Mahmood | S4 — AI Sustainability Coach & Reports |

Confirm the spellings and role assignments with your team before submission.

## Implemented OOP classes

All classes are in `subsystem3/models.py`. Each class has a constructor, initialization/configuration logic, getters and setters, and validation where appropriate.

- `EnergySettings`: building electricity price, emission factor and source.
- `EnergyAnalytics`: energy quantity and period; calculates cost and carbon.
- `SustainabilityScore`: score inputs and score calculation (0–100).
- `EnergyGoal`: monthly target and daily limit; calculates progress.
- `EnergyAlert`: alert message/read status and mark-read behavior.

See `docs/uml_subsystem3.puml` for the editable PlantUML class diagram and `docs/uml_subsystem3.svg` for a rendered diagram.

## Architecture

- `models.py`: OOP domain model and calculations.
- `db.py`: SQLite schema and persistence helpers.
- `services.py`: application use cases connecting models to data.
- `routes.py`: Flask routes and JSON API.
- `errors.py`: custom validation and lookup exceptions that standardize HTTP handling.
- `templates/` and `static/`: simple web dashboard.
- `tests/`: unit and API tests.

## Error handling approach

This project follows the Python exception model from the official tutorial: raise explicit exceptions for invalid input, lookup misses, and permission failures, then translate them into consistent HTTP responses in the Flask blueprint. Each domain area (`settings`, `readings`, `goals`, and `alerts`) has a dedicated custom exception type to make failures easier to diagnose and test.

The class model is intentionally separate from Flask so it can be tested without running the web server.

## Formulas and assumptions

- Cost = energy in kWh × price per kWh.
- Carbon = energy in kWh × emission factor in kg CO₂/kWh.
- Goal progress (%) = consumed kWh ÷ target kWh × 100; progress is not capped, so over-target usage is visible.
- Sustainability score is an illustrative project heuristic, not an official certification: up to 70 points for staying within the monthly target and up to 30 points for reducing emissions versus the previous month. If no previous emissions are supplied, the reduction component is 15 points (neutral baseline). Score is clamped to 0–100.
- Month reduction (%) = (previous − current) ÷ previous × 100. If previous is zero, the result is `None` because percentage reduction is undefined.

The emission factor is configurable. The seeded value is for demonstration only and is not presented as an official German grid factor.

## Run locally (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open http://127.0.0.1:5000.

To add demo data, in another terminal run:

```powershell
.venv\Scripts\Activate.ps1
python seed_demo.py
```

Demo data uses owner ID `1`, building ID `1`.

## Run tests

```powershell
python -m pytest -v
```

Tests use a temporary SQLite database. Run them locally to obtain actual test results; this repository does not claim tests passed unless you run the command and see the result.

## Docker

```bash
docker compose up --build
```

Open http://127.0.0.1:5000. The SQLite database is stored in the `data` volume.

## API overview

The standalone demo uses `X-User-ID` to simulate the authenticated user. This is a **development-only adapter**, not production authentication. During integration, replace it with the logged-in identity from Subsystem 1 and verify ownership on every request.

- `GET /health`
- `GET /api/v1/s3/analytics/<building_id>?period=month&date=2026-10-28`
- `GET /api/v1/s3/comparison/<building_id>?month=2026-10`
- `GET /api/v1/s3/score/<building_id>?month=2026-10`
- `PUT /api/v1/s3/settings/<building_id>`
- `PUT /api/v1/s3/goals/<building_id>`
- `GET /api/v1/s3/goals/<building_id>/progress?month=2026-10`
- `GET /api/v1/s3/alerts?building_id=1`
- `PATCH /api/v1/s3/alerts/<alert_id>/read`
- `DELETE /api/v1/s3/alerts/<alert_id>`
- `POST /api/v1/s3/evaluate-alert/<building_id>?date=2026-10-28`

## GitHub Homeassignment1 branch

From the project directory, connect your GitHub repository as `origin` first, then run:

```bash
git init
git switch -c Homeassignment1
git add .
git commit -m "Refactor Subsystem 3 into OOP domain classes"
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin Homeassignment1
```

If your repository already exists and has a remote, do not repeat `git init` or `git remote add origin`. Create/switch to the branch and push it.

## Team video presentation

Add the real video URL here after the team records and uploads the 3–5 minute presentation:

**Presentation:** TODO — replace with the direct YouTube/Loom/Drive URL.

Do not submit the placeholder as if it were a real link.

## Before submission checklist

- [ ] Confirm team names and assigned subsystems.
- [ ] Review the UML diagram against the team's approved architecture.
- [ ] Run `python -m pytest -v` and record the actual result.
- [ ] Push the code to `Homeassignment1`.
- [ ] Replace the presentation placeholder with the real video URL.
- [ ] Integrate identity and canonical readings from Subsystems 1 and 2 before production use.
