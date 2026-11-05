import math

from flask import Blueprint, jsonify, request
from sqlalchemy import func
from database import db
from models import EnergyReading

energy_bp = Blueprint("energy_api", __name__, url_prefix="/api")

#  WAJIHAH KAINAT ( Get all readings)
@energy_bp.get("/readings")
def get_readings():
    rows = EnergyReading.query.order_by(EnergyReading.recorded_at.desc()).all()
    return jsonify({"status": "success", "count": len(rows),
                    "data": [row.to_dict() for row in rows]})

#  Arshia Fatima ( Get Reading by ID)
@energy_bp.get("/readings/<int:reading_id>")
def get_reading(reading_id):
    row = db.session.get(EnergyReading, reading_id)
    if row is None:
        return jsonify({"status": "error", "message": "Reading not found"}), 404
    return jsonify({"status": "success", "data": row.to_dict()})


# PERSON 3  (Create reading)
@energy_bp.post("/readings")
def create_reading():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"status": "error",
                        "message": "Request body must be a JSON object"}), 400
    required = ["meter_id", "device_type", "power_kw", "energy_kwh"]
    missing = [key for key in required if key not in data]
    if missing:
        return jsonify({"status": "error", "message": "Missing required fields",
                        "fields": missing}), 400
    try:
        if isinstance(data["power_kw"], bool) or isinstance(data["energy_kwh"], bool):
            raise ValueError
        power, energy = float(data["power_kw"]), float(data["energy_kwh"])
        if not math.isfinite(power) or not math.isfinite(energy) or power < 0 or energy < 0:
            raise ValueError
    except (OverflowError, TypeError, ValueError):
        return jsonify({"status": "error",
                        "message": "power_kw and energy_kwh must be non-negative numbers"}), 400

    if not isinstance(data["meter_id"], str) or not isinstance(data["device_type"], str):
        return jsonify({"status": "error",
                        "message": "meter_id and device_type must be strings"}), 400
    meter_id = data["meter_id"].strip()
    device_type = data["device_type"].strip()
    if not meter_id or not device_type:
        return jsonify({"status": "error",
                        "message": "meter_id and device_type cannot be empty"}), 400

    active = data.get("active", True)
    if not isinstance(active, bool):
        return jsonify({"status": "error", "message": "active must be a boolean"}), 400

    row = EnergyReading(meter_id=meter_id, device_type=device_type,
                        power_kw=power, energy_kwh=energy,
                        active=active)
    db.session.add(row)
    db.session.commit()
    return jsonify({"status": "success", "data": row.to_dict()}), 201

#  Person 4 ( Get Statistics)
@energy_bp.get("/statistics")
def get_statistics():
    count, total, average = db.session.query(
        func.count(EnergyReading.id),
        func.coalesce(func.sum(EnergyReading.energy_kwh), 0),
        func.coalesce(func.avg(EnergyReading.power_kw), 0)
    ).one()
    return jsonify({"status": "success", "data": {
        "reading_count": count,
        "total_energy_kwh": round(float(total), 3),
        "average_power_kw": round(float(average), 3)
    }})
