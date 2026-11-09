# Smart Energy: Subsystem 1 (User and Building Management)

Flask + SQLite web application. Part of the AI-Powered Smart Energy Management System.

## What it does
- Register, log in and log out (passwords are stored as hashes)
- Add, edit and delete your own buildings (name, address, type, comfort temperature)
- Add, edit and delete devices inside a building
- Every user sees only their own buildings and devices

## Screens
1. Log in / Register
2. Buildings list (with the add / edit building form)
3. Building details (devices, with the add / edit device form)

## Run on your computer
```
pip install -r requirements.txt
python run.py
```
Open http://127.0.0.1:5000

## Run the tests
```
python -m pytest
```

## Run with Docker
```
docker build -t smart-energy .
docker run -p 5000:5000 -e SECRET_KEY=change-me -v energy-data:/data smart-energy
```

## Settings (environment variables)
| Name | Meaning | Default |
|------|---------|---------|
| SECRET_KEY | signs the login cookie | dev-only-change-me (change it for real use) |
| DATABASE | path of the SQLite file | energy.db |

## Folders
```
app/            the application (s1.py = pages and rules, db.py = database, schema.sql = tables)
app/templates/  HTML pages
app/static/     style.css
tests/          pytest tests
run.py          starts the app
```
