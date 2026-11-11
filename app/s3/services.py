"""Use cases: database persistence + OOP domain model orchestration."""
from datetime import date, timedelta
from app.db import get_db
from app.s3.errors import AppError
from app.s3.models import EnergySettings, EnergyAnalytics, SustainabilityScore, EnergyGoal, EnergyAlert


def _month_range(month):
    try:
        year_s, month_s = month.split("-")
        year, m = int(year_s), int(month_s)
        if not 1 <= m <= 12 or len(year_s) != 4: raise ValueError
    except (AttributeError, ValueError):
        raise ValueError("month must use YYYY-MM format.")
    start = date(year, m, 1)
    end = date(year + (m == 12), 1 if m == 12 else m + 1, 1)
    previous_end = start
    previous_start = date(year - (m == 1), 12 if m == 1 else m - 1, 1)
    return start.isoformat(), end.isoformat(), previous_start.isoformat(), previous_end.isoformat()


def save_settings(owner_id, building_id, price_per_kwh, emission_factor, factor_source):
    ensure_building(owner_id, building_id)
    settings = EnergySettings(int(building_id), price_per_kwh, emission_factor, factor_source)
    db = get_db()
    db.execute("""INSERT INTO energy_settings(owner_id,building_id,price_per_kwh,emission_factor,factor_source)
        VALUES(?,?,?,?,?) ON CONFLICT(owner_id,building_id) DO UPDATE SET
        price_per_kwh=excluded.price_per_kwh, emission_factor=excluded.emission_factor,
        factor_source=excluded.factor_source""",
        (owner_id, building_id, settings.get_price_per_kwh(), settings.get_emission_factor(), settings.get_factor_source()))
    db.commit()
    return settings


def get_settings(owner_id, building_id):
    row = get_db().execute("SELECT * FROM energy_settings WHERE owner_id=? AND building_id=?", (owner_id, building_id)).fetchone()
    if not row: return None
    return EnergySettings(row["building_id"], row["price_per_kwh"], row["emission_factor"], row["factor_source"])


def ensure_building(owner_id, building_id):
    """The building must exist in Subsystem 1 and belong to the user."""
    row = get_db().execute("SELECT id FROM buildings WHERE id=? AND user_id=?",
                           (building_id, owner_id)).fetchone()
    if row is None:
        raise AppError("Building not found.", 404)


def _sum_range(owner_id, building_id, start, end):
    """kWh of a building = sum of the readings of its devices (Subsystem 2)."""
    row = get_db().execute("""SELECT COALESCE(SUM(r.amount_kwh),0) AS kwh
        FROM energy_reading r
        JOIN devices d   ON d.id = r.device_id
        JOIN buildings b ON b.id = d.building_id
        WHERE b.user_id=? AND b.id=? AND r.date>=? AND r.date<?""",
        (owner_id, building_id, start, end)).fetchone()
    return float(row["kwh"])


def analytics(owner_id, building_id, period="month", selected_date=None):
    ensure_building(owner_id, building_id)
    settings = get_settings(owner_id, building_id)
    if settings is None:
        raise AppError("Price and emission factor are not configured for this building.", 404)
    selected = date.fromisoformat(selected_date) if selected_date else date.today()
    if period == "day":
        start, end = selected.isoformat(), (selected + timedelta(days=1)).isoformat()
    elif period == "week":
        monday = selected - timedelta(days=selected.weekday())
        start, end = monday.isoformat(), (monday + timedelta(days=7)).isoformat()
    elif period == "month":
        start, end, _, _ = _month_range(selected.strftime("%Y-%m"))
    else:
        raise AppError("period must be day, week, or month.", 400)
    kwh = _sum_range(owner_id, building_id, start, end)
    calc = EnergyAnalytics(kwh, settings, period)
    return {"owner_id": owner_id, "building_id": building_id, "period": period,
            "start_date": start, "end_date_exclusive": end, "energy_kwh": round(kwh, 3),
            "cost": calc.calculate_cost(), "carbon_kg": calc.calculate_carbon_emissions(),
            "price_per_kwh": settings.get_price_per_kwh(),
            "emission_factor": settings.get_emission_factor(),
            "factor_source": settings.get_factor_source()}


def comparison(owner_id, building_id, month):
    ensure_building(owner_id, building_id)
    settings = get_settings(owner_id, building_id)
    if settings is None:
        raise AppError("Price and emission factor are not configured for this building.", 404)
    start, end, previous_start, previous_end = _month_range(month)
    current_kwh = _sum_range(owner_id, building_id, start, end)
    previous_kwh = _sum_range(owner_id, building_id, previous_start, previous_end)
    current = EnergyAnalytics(current_kwh, settings, "month")
    previous = EnergyAnalytics(previous_kwh, settings, "month")
    current_carbon, previous_carbon = current.calculate_carbon_emissions(), previous.calculate_carbon_emissions()
    reduction = None if previous_carbon == 0 else round((previous_carbon-current_carbon)/previous_carbon*100, 2)
    return {"month": month, "previous_month": previous_start[:7],
            "current_energy_kwh": round(current_kwh, 3), "previous_energy_kwh": round(previous_kwh, 3),
            "current_cost": current.calculate_cost(), "previous_cost": previous.calculate_cost(),
            "current_carbon_kg": current_carbon, "previous_carbon_kg": previous_carbon,
            "carbon_reduction_percent": reduction}


def set_goal(owner_id, building_id, target_kwh, month, daily_limit_kwh):
    ensure_building(owner_id, building_id)
    goal = EnergyGoal(int(owner_id), int(building_id), target_kwh, month, daily_limit_kwh)
    db = get_db()
    db.execute("""INSERT INTO energy_goals(owner_id,building_id,target_kwh,month,daily_limit_kwh)
        VALUES(?,?,?,?,?) ON CONFLICT(owner_id,building_id,month) DO UPDATE SET
        target_kwh=excluded.target_kwh,daily_limit_kwh=excluded.daily_limit_kwh""",
        (owner_id, building_id, goal.get_target_kwh(), goal.get_month(), goal.get_daily_limit_kwh()))
    db.commit()
    return goal


def get_goal(owner_id, building_id, month):
    row = get_db().execute("SELECT * FROM energy_goals WHERE owner_id=? AND building_id=? AND month=?",
                           (owner_id, building_id, month)).fetchone()
    if not row: return None
    return EnergyGoal(row["owner_id"], row["building_id"], row["target_kwh"], row["month"], row["daily_limit_kwh"])


def goal_progress(owner_id, building_id, month):
    ensure_building(owner_id, building_id)
    goal = get_goal(owner_id, building_id, month)
    if goal is None:
        raise AppError("No goal is configured for this building and month.", 404)
    start, end, _, _ = _month_range(month)
    used = _sum_range(owner_id, building_id, start, end)
    return {"month": month, "target_kwh": goal.get_target_kwh(), "consumed_kwh": round(used, 3),
            "progress_percent": goal.calculate_progress(used), "remaining_kwh": round(max(0, goal.get_target_kwh()-used), 3),
            "daily_limit_kwh": goal.get_daily_limit_kwh()}


def evaluate_daily_alert(owner_id, building_id, selected_date):
    ensure_building(owner_id, building_id)
    try: date.fromisoformat(selected_date)
    except (TypeError, ValueError):
        raise AppError("date must use YYYY-MM-DD format.", 400)
    month = selected_date[:7]
    goal = get_goal(owner_id, building_id, month)
    if goal is None:
        raise AppError("Set a goal and daily limit before evaluating alerts.", 404)
    daily_kwh = _sum_range(owner_id, building_id, selected_date, (date.fromisoformat(selected_date)+timedelta(days=1)).isoformat())
    if not goal.is_daily_limit_exceeded(daily_kwh):
        return {"alert_created": False, "daily_kwh": round(daily_kwh, 3), "daily_limit_kwh": goal.get_daily_limit_kwh()}
    db = get_db()
    message = f"Daily energy use {daily_kwh:.2f} kWh exceeded the limit of {goal.get_daily_limit_kwh():.2f} kWh on {selected_date}."
    existing = db.execute("""SELECT id FROM energy_alerts WHERE owner_id=? AND building_id=? AND created_at LIKE ? AND message=?""",
                           (owner_id, building_id, selected_date+"%", message)).fetchone()
    if existing:
        return {"alert_created": False, "alert_id": existing["id"], "daily_kwh": round(daily_kwh, 3), "daily_limit_kwh": goal.get_daily_limit_kwh()}
    alert = EnergyAlert(owner_id, building_id, message, selected_date, False)
    cur = db.execute("INSERT INTO energy_alerts(owner_id,building_id,message,created_at,is_read) VALUES(?,?,?,?,?)",
                     (alert.get_owner_id(), alert.get_building_id(), alert.get_message(), alert.get_created_at(), int(alert.get_is_read())))
    db.commit()
    return {"alert_created": True, "alert_id": cur.lastrowid, "daily_kwh": round(daily_kwh, 3), "daily_limit_kwh": goal.get_daily_limit_kwh()}


def list_alerts(owner_id, building_id=None):
    db = get_db()
    if building_id is None:
        rows = db.execute("SELECT * FROM energy_alerts WHERE owner_id=? ORDER BY id DESC", (owner_id,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM energy_alerts WHERE owner_id=? AND building_id=? ORDER BY id DESC",
                          (owner_id, building_id)).fetchall()
    return [dict(r) for r in rows]


def mark_alert_read(owner_id, alert_id):
    db = get_db()
    row = db.execute("SELECT * FROM energy_alerts WHERE owner_id=? AND id=?", (owner_id, alert_id)).fetchone()
    if not row:
        raise AppError("Alert not found.", 404)
    alert = EnergyAlert(row["owner_id"], row["building_id"], row["message"], row["created_at"], bool(row["is_read"]))
    alert.mark_read()
    db.execute("UPDATE energy_alerts SET is_read=1 WHERE owner_id=? AND id=?", (owner_id, alert_id))
    db.commit()
    return True


def delete_alert(owner_id, alert_id):
    db = get_db()
    cur = db.execute("DELETE FROM energy_alerts WHERE owner_id=? AND id=?", (owner_id, alert_id))
    db.commit()
    if cur.rowcount == 0:
        raise AppError("Alert not found.", 404)
    return True
