from datetime import date
from flask import Blueprint, jsonify, request, render_template, current_app
from . import services
from .errors import AppError

bp = Blueprint("subsystem3", __name__, static_folder="static", template_folder="templates")

def _owner_id():
    # Development-only identity adapter. Replace with Subsystem 1's authenticated identity.
    raw = request.headers.get("X-User-ID", "1" if current_app.config.get("TESTING") else "")
    if not raw:
        raise AppError("Missing X-User-ID header (development adapter).", 403)
    try:
        value = int(raw)
        if value <= 0: raise ValueError
        return value
    except ValueError:
        raise AppError("X-User-ID must be a positive integer.", 403)

def _json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise AppError("Request body must be a JSON object.", 400)
    return data

@bp.errorhandler(AppError)
def handle_app_error(error):
    return jsonify({"error": str(error)}), getattr(error, "status_code", 500)

@bp.errorhandler(ValueError)
def handle_value_error(error):
    return jsonify({"error": str(error)}), 400

@bp.errorhandler(LookupError)
def handle_lookup_error(error):
    return jsonify({"error": str(error)}), 404

@bp.get("/")
def dashboard():
    return render_template("dashboard.html")

@bp.get("/health")
def health():
    return jsonify({"status": "ok", "subsystem": "3"})

@bp.put("/api/v1/s3/settings/<int:building_id>")
def update_settings(building_id):
    data = _json_body()
    required = ("price_per_kwh", "emission_factor", "factor_source")
    missing = [k for k in required if k not in data]
    if missing:
        raise AppError("Missing fields: " + ", ".join(missing), 400)
    settings = services.save_settings(_owner_id(), building_id, data["price_per_kwh"], data["emission_factor"], data["factor_source"])
    return jsonify({"building_id": settings.get_building_id(), "price_per_kwh": settings.get_price_per_kwh(),
                    "emission_factor": settings.get_emission_factor(), "factor_source": settings.get_factor_source()})

@bp.post("/api/v1/s3/readings")
def create_reading():
    data = _json_body()
    for field in ("building_id", "reading_date", "amount_kwh"):
        if field not in data:
            raise AppError(f"Missing field: {field}", 400)
    services.add_reading(_owner_id(), int(data["building_id"]), data["reading_date"], data["amount_kwh"], data.get("is_simulated", False))
    return jsonify({"message": "Reading created"}), 201

@bp.get("/api/v1/s3/analytics/<int:building_id>")
def get_analytics(building_id):
    period = request.args.get("period", "month")
    selected = request.args.get("date", date.today().isoformat())
    return jsonify(services.analytics(_owner_id(), building_id, period, selected))

@bp.get("/api/v1/s3/comparison/<int:building_id>")
def get_comparison(building_id):
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    return jsonify(services.comparison(_owner_id(), building_id, month))

@bp.get("/api/v1/s3/score/<int:building_id>")
def get_score(building_id):
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    comp = services.comparison(_owner_id(), building_id, month)
    goal = services.goal_progress(_owner_id(), building_id, month)
    from .models import SustainabilityScore
    score = SustainabilityScore(goal["consumed_kwh"], goal["target_kwh"], comp["current_carbon_kg"], comp["previous_carbon_kg"])
    return jsonify({"month": month, "score": score.calculate_score(), "formula_note": "Illustrative MVP heuristic; not an official certification."})

@bp.put("/api/v1/s3/goals/<int:building_id>")
def update_goal(building_id):
    data = _json_body()
    required = ("target_kwh", "month", "daily_limit_kwh")
    missing = [k for k in required if k not in data]
    if missing:
        raise AppError("Missing fields: " + ", ".join(missing), 400)
    goal = services.set_goal(_owner_id(), building_id, data["target_kwh"], data["month"], data["daily_limit_kwh"])
    return jsonify({"building_id": goal.get_building_id(), "month": goal.get_month(),
                    "target_kwh": goal.get_target_kwh(), "daily_limit_kwh": goal.get_daily_limit_kwh()})

@bp.get("/api/v1/s3/goals/<int:building_id>/progress")
def get_progress(building_id):
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    return jsonify(services.goal_progress(_owner_id(), building_id, month))

@bp.post("/api/v1/s3/evaluate-alert/<int:building_id>")
def evaluate_alert(building_id):
    selected = request.args.get("date", date.today().isoformat())
    return jsonify(services.evaluate_daily_alert(_owner_id(), building_id, selected))

@bp.get("/api/v1/s3/alerts")
def get_alerts():
    building = request.args.get("building_id", type=int)
    return jsonify({"alerts": services.list_alerts(_owner_id(), building)})

@bp.patch("/api/v1/s3/alerts/<int:alert_id>/read")
def read_alert(alert_id):
    services.mark_alert_read(_owner_id(), alert_id)
    return jsonify({"message": "Alert marked as read."})

@bp.delete("/api/v1/s3/alerts/<int:alert_id>")
def remove_alert(alert_id):
    services.delete_alert(_owner_id(), alert_id)
    return jsonify({"message": "Alert deleted."})
