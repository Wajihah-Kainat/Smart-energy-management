# Assignment 3 – Smart Energy Management Web API

**Assignment:** Hometask 3 – Web APIs & Database Access Layers  
**Framework:** Flask | **Database:** MySQL | **Domain:** Smart Energy Management

This is a standalone Assignment 3 implementation. It uses the Smart Energy Management domain but does not depend on the code or runtime of Assignments 1 and 2.

## Purpose
Create a Flask application connected to MySQL and expose stored energy-meter readings through HTTP APIs and a simple browser page.

## Structure
```text
assignment3/
├── app.py
├── config.py
├── database.py
├── models.py
├── routes.py
├── templates/index.html
├── static/style.css
├── database/schema.sql
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup
Requirements: Python 3.10+, MySQL Server and pip.

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows PowerShell: .venv\\Scripts\\Activate.ps1
   # macOS/Linux: source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run `database/schema.sql` in MySQL Workbench, or:
   ```bash
   mysql -u YOUR_USER -p < database/schema.sql
   ```
4. Copy `.env.example` to `.env` and set your MySQL credentials:
   ```text
   DATABASE_URL=mysql+pymysql://YOUR_USER:YOUR_PASSWORD@localhost:3306/smart_energy_assignment3
   ```
5. Start Flask:
   ```bash
   python app.py
   ```
6. Visit http://127.0.0.1:5000/.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Application health |
| GET | `/api/readings` | Retrieve all readings |
| GET | `/api/readings/<id>` | Retrieve one reading |
| POST | `/api/readings` | Insert a reading |
| GET | `/api/statistics` | Count, total energy and average power |

## Browser page
- Use **View** beside a reading to retrieve and display its full details.
- Use **Add reading** to submit a reading through `POST /api/readings`; the readings and statistics refresh after it is saved.
- Refresh the readings and statistics independently with their respective buttons.

### POST example
Send JSON to `POST http://127.0.0.1:5000/api/readings`:
```json
{
  "meter_id": "HVAC-004",
  "device_type": "HVAC",
  "power_kw": 5.8,
  "energy_kwh": 1.25,
  "active": true
}
```

## Database access layer
- `database.py`: shared SQLAlchemy database object.
- `models.py`: `EnergyReading` ORM model and JSON conversion.
- `routes.py`: HTTP endpoints and database queries.
- `config.py`: loads the connection string from environment variables.

## GitHub: same repository, separate branch

From the main repository root, create a dedicated branch:
```bash
git switch main
git pull
git switch -c Homeassignment3
```
Copy the `assignment3` folder into the repository root, then:
```bash
git add assignment3
git commit -m "Add Assignment 3 Flask MySQL web API"
git push -u origin Homeassignment3
```
Use the exact branch name required by your course if it differs.

## Notes
- Do not commit `.env` or real database passwords.
- Run the SQL script before starting the app; the app does not create the database automatically.
- Update the connection URL to match your local MySQL credentials.

## Presentation Link
