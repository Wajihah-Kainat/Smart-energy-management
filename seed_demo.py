# Fills the database with demo data so every page has something to show.
# Run:  python seed_demo.py      then log in with demo@example.com / demo12345
import random
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

from app import create_app, db


def seed():
    app = create_app()
    with app.app_context():
        conn = db.get_db()
        if conn.execute("SELECT 1 FROM users WHERE email = 'demo@example.com'").fetchone():
            print("Demo data already exists.")
            return
        today = date.today()
        user_id = conn.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            ("Anna Becker", "demo@example.com", generate_password_hash("demo12345"), today.isoformat())).lastrowid
        random.seed(7)
        for name, address, kind, temp, devices in [
            ("Main office", "Emil-Figge-Str. 42, Dortmund", "office", 21,
             [("Heat pump", "electricity"), ("Lighting", "electricity"), ("Server room", "electricity")]),
            ("Campus lab", "Otto-Hahn-Str. 10, Dortmund", "university", 20,
             [("Air conditioner", "electricity"), ("Lab equipment", "electricity")]),
        ]:
            building_id = conn.execute(
                "INSERT INTO buildings (user_id, name, address, type, comfort_temp) VALUES (?, ?, ?, ?, ?)",
                (user_id, name, address, kind, temp)).lastrowid
            for device_name, energy_type in devices:
                device_id = conn.execute(
                    "INSERT INTO devices (building_id, name, energy_type) VALUES (?, ?, ?)",
                    (building_id, device_name, energy_type)).lastrowid
                for days_ago in range(0, 60):
                    day = today - timedelta(days=days_ago)
                    base = 4.0 if "Heat" in device_name or "Air" in device_name else 2.0
                    amount = round(base * random.uniform(0.7, 1.3) * (1.1 if days_ago < 30 else 1.0), 2)
                    conn.execute(
                        "INSERT INTO energy_reading (device_id, date, amount_kwh, is_simulated) VALUES (?, ?, ?, 0)",
                        (device_id, day.isoformat(), amount))
            conn.execute(
                "INSERT INTO energy_settings (owner_id, building_id, price_per_kwh, emission_factor, factor_source) "
                "VALUES (?, ?, 0.30, 0.40, 'Illustrative demo value')", (user_id, building_id))
            conn.execute(
                "INSERT INTO energy_goals (owner_id, building_id, target_kwh, month, daily_limit_kwh) VALUES (?, ?, ?, ?, ?)",
                (user_id, building_id, 450 if kind == "office" else 300, today.strftime("%Y-%m"), 14 if kind == "office" else 10))
        conn.commit()
        print("Demo data created. Log in with demo@example.com / demo12345")


if __name__ == "__main__":
    seed()
