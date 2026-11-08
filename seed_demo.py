"""Create repeatable demo data for owner 1 / building 1."""
from datetime import date, timedelta
from subsystem3 import create_app
from subsystem3.db import get_db
from subsystem3 import services

app = create_app()
with app.app_context():
    services.save_settings(1, 1, 0.30, 0.40, "Illustrative demo value; replace with a cited source")
    month = date.today().strftime("%Y-%m")
    services.set_goal(1, 1, 300, month, 20)
    db = get_db()
    # Avoid seeding duplicates for the same demo dates.
    for days_ago, amount in [(2, 12.5), (1, 18.0), (0, 22.0)]:
        d = (date.today() - timedelta(days=days_ago)).isoformat()
        exists = db.execute("SELECT 1 FROM energy_readings WHERE owner_id=1 AND building_id=1 AND reading_date=? AND is_simulated=1", (d,)).fetchone()
        if not exists:
            services.add_reading(1, 1, d, amount, True)
    print("Demo data ready for owner 1 / building 1.")
