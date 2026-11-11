"""Routes for Energy Monitoring and Dashboard."""
import random
import csv
import io

from flask import Response

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    Response,
    jsonify,
)

from database import get_connection
from models.energy_reading import (
    list_readings,
    add_reading,
    update_reading,
    delete_reading,
)


monitoring_bp = Blueprint("monitoring", __name__)


@monitoring_bp.route("/readings", methods=["GET", "POST"])
def readings():


    # ADD NEW ENERGY READING

    if request.method == "POST":
        try:
            device_id = int(request.form["device_id"])
            reading_date = request.form["date"]
            amount_kwh = request.form["amount_kwh"]

            add_reading(
                device_id=device_id,
                reading_date=reading_date,
                amount_kwh=amount_kwh,
            )

            flash(
                "Energy reading added successfully!",
                "success",
            )

        except (ValueError, KeyError) as error:
            flash(str(error), "error")

        return redirect(url_for("monitoring.readings"))

    # ---------------------------------
    # GET FILTER VALUES
    # ---------------------------------

    device_filter = request.args.get(
        "device_id",
        "",
    )

    date_from = request.args.get(
        "date_from",
        "",
    )

    date_to = request.args.get(
        "date_to",
        "",
    )

    # ---------------------------------
    # LOAD DEVICES
    # ---------------------------------

    with get_connection() as connection:

        devices = connection.execute(
            """
            SELECT id, name
            FROM demo_devices
            ORDER BY name
            """
        ).fetchall()

        # ---------------------------------
        # BUILD FILTER QUERY
        # ---------------------------------

        query = """
            SELECT
                r.id,
                r.device_id,
                d.name AS device_name,
                r.date,
                r.amount_kwh,
                r.is_simulated

            FROM energy_reading AS r

            JOIN demo_devices AS d
                ON d.id = r.device_id

            WHERE 1 = 1
        """

        parameters = []

        # Filter by device
        if device_filter:

            query += """
                AND r.device_id = ?
            """

            parameters.append(
                int(device_filter)
            )

        # Filter from date
        if date_from:

            query += """
                AND r.date >= ?
            """

            parameters.append(
                date_from
            )

        # Filter until date
        if date_to:

            query += """
                AND r.date <= ?
            """

            parameters.append(
                date_to
            )

        query += """
            ORDER BY
                r.date DESC,
                r.id DESC
        """

        readings_list = connection.execute(
            query,
            parameters,
        ).fetchall()

    return render_template(
        "readings.html",
        devices=devices,
        readings=readings_list,
        selected_device=device_filter,
        date_from=date_from,
        date_to=date_to,
    )

@monitoring_bp.route(
    "/readings/edit/<int:reading_id>",
    methods=["GET", "POST"],
)
def edit_reading(reading_id):

    with get_connection() as connection:
        reading = connection.execute(
            """
            SELECT id, device_id, date, amount_kwh
            FROM energy_reading
            WHERE id = ?
            """,
            (reading_id,),
        ).fetchone()

        devices = connection.execute(
            """
            SELECT id, name
            FROM demo_devices
            ORDER BY name
            """
        ).fetchall()

    if reading is None:
        flash("Reading does not exist.", "error")
        return redirect(url_for("monitoring.readings"))

    if request.method == "POST":
        try:
            device_id = int(request.form["device_id"])
            reading_date = request.form["date"]
            amount_kwh = request.form["amount_kwh"]

            update_reading(
                reading_id=reading_id,
                device_id=device_id,
                reading_date=reading_date,
                amount_kwh=amount_kwh,
            )

            flash(
                "Reading updated successfully!",
                "success",
            )

            return redirect(
                url_for("monitoring.readings")
            )

        except (ValueError, KeyError) as error:
            flash(str(error), "error")

    return render_template(
        "edit_reading.html",
        reading=reading,
        devices=devices,
    )
@monitoring_bp.route("/readings/export")
def export_readings():
    """Export readings using the same filters as the readings page."""

    device_filter = request.args.get("device_id", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()

    query = """
        SELECT
            r.id,
            d.name AS device_name,
            r.date,
            r.amount_kwh,
            r.is_simulated
        FROM energy_reading AS r
        JOIN demo_devices AS d
            ON d.id = r.device_id
        WHERE 1 = 1
    """
    parameters = []

    if device_filter:
        query += " AND r.device_id = ?"
        parameters.append(int(device_filter))

    if date_from:
        query += " AND r.date >= ?"
        parameters.append(date_from)

    if date_to:
        query += " AND r.date <= ?"
        parameters.append(date_to)

    query += " ORDER BY r.date ASC, r.id ASC"

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Device",
        "Date",
        "Consumption (kWh)",
        "Type",
    ])

    for row in rows:
        writer.writerow([
            row["id"],
            row["device_name"],
            row["date"],
            row["amount_kwh"],
            "Simulated" if row["is_simulated"] else "Real",
        ])

    csv_data = output.getvalue()

    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=energy_readings.csv"
        },
    )
@monitoring_bp.route(
    "/readings/simulate",
    methods=["POST"],
)
def simulate_reading():
    """Create one simulated energy reading."""

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No simulation data received."
            }), 400

        device_id = int(data["device_id"])

        # Create a random simulated consumption value
        amount_kwh = round(
            random.uniform(0.2, 2.0),
            2
        )

        # Use today's date
        from datetime import date

        reading_date = date.today().isoformat()

        reading_id = add_reading(
            device_id=device_id,
            reading_date=reading_date,
            amount_kwh=amount_kwh,
            is_simulated=True,
        )

        with get_connection() as connection:
            reading = connection.execute(
                """
                SELECT
                    r.id,
                    r.device_id,
                    d.name AS device_name,
                    r.date,
                    r.amount_kwh,
                    r.is_simulated
                FROM energy_reading AS r
                JOIN demo_devices AS d
                    ON d.id = r.device_id
                WHERE r.id = ?
                """,
                (reading_id,),
            ).fetchone()

        return jsonify({
            "success": True,
            "reading": {
                "id": reading["id"],
                "device_name": reading["device_name"],
                "date": reading["date"],
                "amount_kwh": reading["amount_kwh"],
                "type": "Simulated",
            }
        })

    except (ValueError, KeyError) as error:

        return jsonify({
            "success": False,
            "message": str(error),
        }), 400
# ---------------------------------
# DELETE READING
# ---------------------------------

@monitoring_bp.route(
    "/readings/delete/<int:reading_id>",
    methods=["POST"],
)
def remove_reading(reading_id):

    try:

        delete_reading(reading_id)

        flash(
            "Reading deleted successfully!",
            "success",
        )

    except ValueError as error:

        flash(
            str(error),
            "error",
        )

    return redirect(
        url_for("monitoring.readings")
    )
