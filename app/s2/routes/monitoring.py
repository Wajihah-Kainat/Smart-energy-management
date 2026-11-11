"""Routes for Energy Monitoring and Dashboard (Subsystem 2).

Integrated version: every page needs a login (Subsystem 1), the devices and
buildings in the forms come from Subsystem 1, and every query is limited to
the logged-in user.
"""
import csv
import io
import random
from datetime import date

from flask import (Blueprint, Response, flash, g, jsonify, redirect,
                   render_template, request, url_for)

from app.s1 import login_required
from app.s2.models.energy_reading import (
    add_reading,
    delete_reading,
    get_reading,
    list_devices,
    list_readings,
    update_reading,
)
from app.s2.services.statistics import Statistics
from app.db import get_db

monitoring_bp = Blueprint("monitoring", __name__)


def _user_id():
    return g.user["id"]


def _own_buildings():
    return get_db().execute(
        "SELECT id, name FROM buildings WHERE user_id = ? ORDER BY name",
        (_user_id(),)).fetchall()


def _filters():
    return (request.args.get("device_id", "").strip(),
            request.args.get("date_from", "").strip(),
            request.args.get("date_to", "").strip())


# ---------------------------------
# DASHBOARD (charts and totals)
# ---------------------------------
@monitoring_bp.route("/dashboard")
@login_required
def dashboard():
    building_id = request.args.get("building_id", type=int)
    statistics = Statistics(user_id=_user_id(), building_id=building_id)
    return render_template(
        "s2/dashboard.html",
        buildings=_own_buildings(),
        selected_building=building_id,
        daily_totals=statistics.total_per_day(),
        weekly_totals=statistics.total_per_week(),
        monthly_totals=statistics.total_per_month(),
        total_consumption=statistics.total_consumption(),
        reading_count=statistics.reading_count(),
        device_count=statistics.device_count(),
    )


# ---------------------------------
# LIST + ADD READINGS
# ---------------------------------
@monitoring_bp.route("/readings", methods=["GET", "POST"])
@login_required
def readings():
    if request.method == "POST":
        try:
            add_reading(
                device_id=int(request.form["device_id"]),
                reading_date=request.form["date"],
                amount_kwh=request.form["amount_kwh"],
                user_id=_user_id(),
            )
            flash("Energy reading added successfully!", "ok")
        except (ValueError, KeyError) as error:
            flash(str(error), "error")
        return redirect(url_for("monitoring.readings"))

    device_filter, date_from, date_to = _filters()
    return render_template(
        "s2/readings.html",
        devices=list_devices(user_id=_user_id()),
        readings=list_readings(user_id=_user_id(), device_id=device_filter,
                               date_from=date_from, date_to=date_to),
        selected_device=device_filter,
        date_from=date_from,
        date_to=date_to,
        today=date.today().isoformat(),
    )


@monitoring_bp.route("/readings/edit/<int:reading_id>", methods=["GET", "POST"])
@login_required
def edit_reading(reading_id):
    reading = get_reading(reading_id, user_id=_user_id())
    if reading is None:
        flash("Reading does not exist.", "error")
        return redirect(url_for("monitoring.readings"))

    if request.method == "POST":
        try:
            update_reading(
                reading_id=reading_id,
                device_id=int(request.form["device_id"]),
                reading_date=request.form["date"],
                amount_kwh=request.form["amount_kwh"],
                user_id=_user_id(),
            )
            flash("Reading updated successfully!", "ok")
            return redirect(url_for("monitoring.readings"))
        except (ValueError, KeyError) as error:
            flash(str(error), "error")

    return render_template("s2/edit_reading.html", reading=reading,
                           devices=list_devices(user_id=_user_id()))


@monitoring_bp.route("/readings/export")
@login_required
def export_readings():
    """Export readings using the same filters as the readings page."""
    device_filter, date_from, date_to = _filters()
    rows = list_readings(user_id=_user_id(), device_id=device_filter,
                         date_from=date_from, date_to=date_to)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Building", "Device", "Date", "Consumption (kWh)", "Type"])
    for row in reversed(rows):                      # oldest first
        writer.writerow([row["id"], row["building_name"], row["device_name"],
                         row["date"], row["amount_kwh"],
                         "Simulated" if row["is_simulated"] else "Real"])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=energy_readings.csv"},
    )


@monitoring_bp.route("/readings/simulate", methods=["POST"])
@login_required
def simulate_reading():
    """Create one simulated energy reading."""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False,
                            "message": "No simulation data received."}), 400

        amount_kwh = round(random.uniform(0.2, 2.0), 2)
        reading_id = add_reading(
            device_id=int(data["device_id"]),
            reading_date=date.today().isoformat(),
            amount_kwh=amount_kwh,
            is_simulated=True,
            user_id=_user_id(),
        )
        row = next(r for r in list_readings(user_id=_user_id()) if r["id"] == reading_id)
        return jsonify({"success": True, "reading": {
            "id": row["id"], "device_name": row["device_name"], "date": row["date"],
            "amount_kwh": row["amount_kwh"], "type": "Simulated"}})

    except (ValueError, KeyError, TypeError) as error:
        return jsonify({"success": False, "message": str(error)}), 400


@monitoring_bp.route("/readings/delete/<int:reading_id>", methods=["POST"])
@login_required
def remove_reading(reading_id):
    try:
        delete_reading(reading_id, user_id=_user_id())
        flash("Reading deleted successfully!", "ok")
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("monitoring.readings"))
