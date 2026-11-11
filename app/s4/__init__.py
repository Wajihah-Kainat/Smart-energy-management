"""Subsystem 4: AI Coach and Reports.

Integrated version: the buildings come from Subsystem 1, the energy from
Subsystem 2 and cost, carbon, goal and score from Subsystem 3.
"""
import io
from datetime import date

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   send_file, url_for)

from app.s1 import login_required
from app.s4 import data
from app.s4.models import (AICoachService, DatabaseManager, ReportGenerator,
                           Subsystem4Exception)

bp = Blueprint("s4", __name__)

db_manager = DatabaseManager()
ai_coach = AICoachService()
report_generator = ReportGenerator()


def _current_month():
    return date.today().strftime("%Y-%m")


def _parse_choice(buildings, months):
    """Read building and period from the form; fall back to the first building / current month."""
    building_id = request.values.get("building_id", type=int)
    if building_id not in [b["id"] for b in buildings]:
        building_id = buildings[0]["id"] if buildings else None
    month = request.values.get("period", _current_month())
    if month not in months:
        month = _current_month()
    return building_id, month


# ------------------------------------------------------------------ AI coach
@bp.route("/coach", methods=["GET", "POST"])
@login_required
def coach():
    user_id = g.user["id"]
    buildings = data.own_buildings(user_id)
    months = data.available_months(user_id, _current_month())
    building_id, month = _parse_choice(buildings, months)

    summary, ai_tips, error = None, [], None
    if building_id:
        summary = data.building_summary(user_id, building_id, month)
        if request.method == "POST":
            try:
                tip = ai_coach.generate_coach_tips(
                    data.daily_average(summary), data.coach_context(summary))
                ai_tips = [tip]
            except Subsystem4Exception:
                error = "AI service is currently unavailable. Please try again later."

    return render_template("s4/coach.html", buildings=buildings, months=months,
                           building_id=building_id, month=month, summary=summary,
                           ai_tips=ai_tips, error=error, has_key=ai_coach.has_key(),
                           tip_label=ai_coach.source_label() if ai_tips else None)


# ------------------------------------------------------------------ reports
def _report_lines(summary):
    lines = [f"Building: {summary['building_name']} ({summary['building_type']})",
             f"Address: {summary['address']}",
             f"Comfort temperature: {summary['comfort_temp']:g} C",
             f"Period: {summary['month']}",
             f"Energy: {summary['energy_kwh']} kWh"]
    if summary["previous_kwh"] is not None:
        lines.append(f"Month before: {summary['previous_kwh']} kWh")
    if summary["configured"]:
        lines += [f"Cost: {summary['cost']:.2f} EUR", f"Carbon: {summary['carbon_kg']:.2f} kg CO2"]
    else:
        lines.append("Cost and carbon: price and emission factor are not set (Costs & Carbon page).")
    if summary["goal_percent"] is not None:
        lines.append(f"Goal: {summary['goal_percent']}% of {summary['goal_target']} kWh used")
    if summary["score"] is not None:
        lines.append(f"Sustainability score: {summary['score']}/100")
    return lines


@bp.route("/reports", methods=["GET", "POST"])
@login_required
def reports():
    user_id = g.user["id"]
    buildings = data.own_buildings(user_id)
    months = data.available_months(user_id, _current_month())

    if request.method == "POST":
        building_id, month = _parse_choice(buildings, months)
        if building_id is None:
            flash("Add a building first.", "error")
        else:
            db_manager.add_report(user_id, building_id, month)
            flash("Report created.", "ok")
        return redirect(url_for("s4.reports"))

    rows = []
    for report in db_manager.list_reports(user_id):
        summary = data.building_summary(user_id, report["building_id"], report["period"])
        rows.append({"report": report, "summary": summary})
    return render_template("s4/reports.html", buildings=buildings, months=months,
                           month=_current_month(), rows=rows)


@bp.route("/reports/<int:report_id>/pdf")
@login_required
def report_pdf(report_id):
    report = db_manager.get_report(g.user["id"], report_id)
    if report is None:
        return render_template("s4/not_found.html"), 404
    summary = data.building_summary(g.user["id"], report["building_id"], report["period"])
    tip = ai_coach.generate_coach_tips(data.daily_average(summary), data.coach_context(summary))
    buffer = io.BytesIO()
    title = ("AI Coach advice (OpenAI):" if ai_coach.last_source == "openai"
             else "Coach advice (built-in tip, no OpenAI answer):")
    report_generator.create_pdf_report(_report_lines(summary), tip, output=buffer, tip_title=title)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, mimetype="application/pdf",
                     download_name=f"energy_report_{report['building']}_{report['period']}.pdf")


@bp.route("/reports/<int:report_id>/delete", methods=["POST"])
@login_required
def report_delete(report_id):
    if db_manager.delete_report(g.user["id"], report_id):
        flash("Report deleted.", "ok")
    return redirect(url_for("s4.reports"))
