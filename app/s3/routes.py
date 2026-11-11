"""Subsystem 3 routes: one HTML page (Costs & Carbon) and the JSON API behind it.

Integrated version:
  * the owner is the logged-in user of Subsystem 1 (no X-User-ID header any more),
  * the building must be one of the user's buildings in Subsystem 1,
  * the kWh values come from the readings of Subsystem 2 (no own readings table).
"""
from datetime import date

from flask import Blueprint, g, jsonify, redirect, render_template, request, url_for

from app.db import get_db
from app.s3 import services
from app.s3.errors import AppError
from app.s3.models import SustainabilityScore

bp = Blueprint("s3", __name__)


def _owner_id():
    if g.user is None:
        raise AppError("Please log in first.", 401)
    return g.user["id"]


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


# ------------------------------------------------------------------ the page
@bp.get("/costs-carbon")
def costs_carbon():
    if g.user is None:
        return redirect(url_for("s1.login"))
    buildings = get_db().execute(
        "SELECT id, name FROM buildings WHERE user_id=? ORDER BY name", (g.user["id"],)).fetchall()
    building_id = request.args.get("building_id", type=int)
    if buildings and building_id not in [b["id"] for b in buildings]:
        building_id = buildings[0]["id"]
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    settings = goal = None
    if building_id:
        settings = services.get_settings(g.user["id"], building_id)
        goal = services.get_goal(g.user["id"], building_id, month)
    return render_template("s3/costs_carbon.html", buildings=buildings, building_id=building_id,
                           month=month, today=date.today().isoformat(),
                           settings=settings, goal=goal)


@bp.get("/health")
def health():
    return jsonify({"status": "ok"})


# ------------------------------------------------------------------ the API
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
