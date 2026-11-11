"""Where Subsystem 4 gets its numbers (nothing is typed in by hand any more).

  Subsystem 1: building (name, type, address, comfort temperature)
  Subsystem 2: energy in kWh per month (readings of the building's devices)
  Subsystem 3: price and carbon factor, goal, cost, carbon, score
"""
from app.db import get_db
from app.s2.services.statistics import Statistics
from app.s3 import services as s3
from app.s3.errors import AppError
from app.s3.models import SustainabilityScore


def own_buildings(user_id):
    return get_db().execute(
        "SELECT * FROM buildings WHERE user_id = ? ORDER BY name", (user_id,)).fetchall()


def own_building(user_id, building_id):
    return get_db().execute(
        "SELECT * FROM buildings WHERE id = ? AND user_id = ?", (building_id, user_id)).fetchone()


def available_months(user_id, current_month):
    """Months that have readings (Subsystem 2), newest first; the current month is always offered."""
    months = {row["period"] for row in Statistics(user_id=user_id).total_per_month()}
    months.add(current_month)
    return sorted(months, reverse=True)


def building_summary(user_id, building_id, month):
    """All numbers of one building in one month, from Subsystems 1, 2 and 3."""
    building = own_building(user_id, building_id)
    if building is None:
        raise LookupError("Building not found.")

    monthly = {row["period"]: row["total_kwh"]
               for row in Statistics(user_id=user_id, building_id=building_id).total_per_month()}
    summary = {
        "building_name": building["name"], "building_type": building["type"],
        "address": building["address"], "comfort_temp": building["comfort_temp"],
        "month": month, "energy_kwh": round(monthly.get(month, 0), 2),
        "previous_kwh": None, "change_percent": None,
        "configured": False, "cost": None, "carbon_kg": None,
        "goal_target": None, "goal_percent": None, "score": None,
    }

    settings = s3.get_settings(user_id, building_id)
    if settings is not None:
        summary["configured"] = True
        analytics = s3.analytics(user_id, building_id, "month", month + "-01")
        comparison = s3.comparison(user_id, building_id, month)
        summary.update(cost=analytics["cost"], carbon_kg=analytics["carbon_kg"],
                       previous_kwh=comparison["previous_energy_kwh"])
        if comparison["previous_energy_kwh"]:
            summary["change_percent"] = round(
                (comparison["current_energy_kwh"] - comparison["previous_energy_kwh"])
                / comparison["previous_energy_kwh"] * 100, 1)
        try:
            goal = s3.goal_progress(user_id, building_id, month)
            summary.update(goal_target=goal["target_kwh"], goal_percent=goal["progress_percent"])
            summary["score"] = SustainabilityScore(
                goal["consumed_kwh"], goal["target_kwh"],
                comparison["current_carbon_kg"], comparison["previous_carbon_kg"]).calculate_score()
        except AppError:
            pass                                     # no goal for this month
    return summary


def daily_average(summary):
    """Average kWh per day of the month (used by the rule-based coach)."""
    return round(summary["energy_kwh"] / 30, 2)


def coach_context(summary):
    """The short summary that is sent to the AI (no name, e-mail or address)."""
    return {"building_type": summary["building_type"], "comfort_temp": summary["comfort_temp"],
            "month": summary["month"],
            "energy_kwh": summary["energy_kwh"], "change_percent": summary["change_percent"],
            "goal_percent": summary["goal_percent"]}
