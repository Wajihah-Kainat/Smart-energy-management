from flask import Flask, render_template

from database import init_db
from routes.monitoring import monitoring_bp
from services.energy_calculator import (
    get_daily_totals,
    get_weekly_totals,
    get_monthly_totals,
    get_total_consumption,
    get_reading_count,
)


def create_app():
    app = Flask(__name__)

    app.config["DATABASE"] = "energy.db"
    app.secret_key = "smart-energy-development-key"

    # Create / initialize the SQLite database
    with app.app_context():
        init_db(app.config["DATABASE"])

    # Register S2 routes
    app.register_blueprint(monitoring_bp)

    @app.get("/")
    def dashboard():
        daily_totals = get_daily_totals()
        weekly_totals = get_weekly_totals()
        monthly_totals = get_monthly_totals()

        total_consumption = get_total_consumption()
        reading_count = get_reading_count()

        return render_template(
            "dashboard.html",
            daily_totals=daily_totals,
            weekly_totals=weekly_totals,
            monthly_totals=monthly_totals,
            total_consumption=total_consumption,
            reading_count=reading_count,
        )

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "subsystem": "S2",
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)