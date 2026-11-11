"""Subsystem 4 classes: report storage, AI coach, PDF report.

Integrated version: reports are stored in the one project database, and the
coach and the report get their numbers from Subsystems 1, 2 and 3 (see data.py)
instead of numbers typed in by hand.
"""
import os
import textwrap
from datetime import date

from app.db import get_db

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class Subsystem4Exception(Exception):
    pass


class DatabaseManager:
    """Saved reports (table `reports`). A report belongs to a user and a building of Subsystem 1."""

    def list_reports(self, user_id):
        return get_db().execute(
            "SELECT r.id, r.building_id, b.name AS building, r.period, r.created_date "
            "FROM reports r JOIN buildings b ON b.id = r.building_id "
            "WHERE r.user_id = ? ORDER BY r.id DESC", (user_id,)).fetchall()

    def get_report(self, user_id, report_id):
        return get_db().execute(
            "SELECT r.id, r.building_id, b.name AS building, r.period, r.created_date "
            "FROM reports r JOIN buildings b ON b.id = r.building_id "
            "WHERE r.user_id = ? AND r.id = ?", (user_id, report_id)).fetchone()

    def add_report(self, user_id, building_id, period):
        db = get_db()
        cursor = db.execute(
            "INSERT INTO reports (user_id, building_id, period, created_date) VALUES (?, ?, ?, ?)",
            (user_id, building_id, period, date.today().isoformat()))
        db.commit()
        return cursor.lastrowid

    def delete_report(self, user_id, report_id):
        db = get_db()
        cursor = db.execute("DELETE FROM reports WHERE user_id = ? AND id = ?", (user_id, report_id))
        db.commit()
        return cursor.rowcount > 0


class AICoachService:
    SOURCE_LABELS = {
        "openai": "Tip by OpenAI (gpt-4o-mini)",
        "rules": "Built-in tip: no OpenAI key is set. Add your key to the .env file (see README).",
        "error": "OpenAI could not be reached. Check your key, your credit and your internet connection.",
    }

    def __init__(self):
        self.client = None
        self.last_source = "rules"      # where the last tip came from: openai / rules / error

    def has_key(self):
        """True when an OpenAI key is available (so the AI will be used)."""
        return self._get_client() is not None

    def source_label(self):
        return self.SOURCE_LABELS[self.last_source]

    def _get_client(self):
        """Create the OpenAI client when it is first needed (the key may come from the .env file)."""
        if self.client is None and OpenAI and os.environ.get("OPENAI_API_KEY"):
            self.client = OpenAI()
        return self.client

    @staticmethod
    def build_prompt(latest_kwh, context=None):
        """Short text for the AI. No name, e-mail or address is included."""
        if not context:
            return f"Latest energy usage is {latest_kwh} kWh. Give a short saving tip."
        parts = [f"Building type: {context['building_type']}.",
                 f"Comfort temperature of the building: {context['comfort_temp']:g} °C.",
                 f"Energy in {context['month']}: {context['energy_kwh']} kWh."]
        if context.get("change_percent") is not None:
            parts.append(f"Change compared with the month before: {context['change_percent']:+.1f}%.")
        if context.get("goal_percent") is not None:
            parts.append(f"{context['goal_percent']}% of the monthly goal is used.")
        return " ".join(parts) + " Give a short saving tip."

    @staticmethod
    def rule_based_tip(latest_kwh, context=None):
        """Tip without AI (used when there is no API key)."""
        if context:
            if context["energy_kwh"] == 0:
                return "No readings found for this period. Record some readings first to get a personal tip."
            if context.get("goal_percent") is not None and context["goal_percent"] > 100:
                return (f"You used {context['goal_percent']}% of your monthly goal. "
                        "Switch off devices that run without need and shift heavy use to off-peak hours.")
            if context.get("change_percent") is not None and context["change_percent"] > 10:
                return (f"Your usage rose {context['change_percent']:.0f}% compared with the month before. "
                        "Check which devices stay on at night or on weekends.")
        if latest_kwh > 20:
            if context:
                return ("Energy usage is high. Keep heating and cooling at your comfort temperature of "
                        f"{context['comfort_temp']:g} °C and shift heavy appliance usage to off-peak hours.")
            return "Energy usage is high. Consider shifting heavy appliance usage to off-peak hours."
        return "Great job! Your energy usage is at an optimal and sustainable level."

    def generate_coach_tips(self, latest_kwh, context=None):
        client = self._get_client()
        if not client:
            self.last_source = "rules"
            return self.rule_based_tip(latest_kwh, context)

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI sustainability coach for an energy management system. Provide 1 brief, practical tip."},
                    {"role": "user", "content": self.build_prompt(latest_kwh, context)}
                ],
                max_tokens=60
            )
            self.last_source = "openai"
            return response.choices[0].message.content.strip()
        except Exception:
            self.last_source = "error"
            return "AI service is currently unavailable. Please maintain current efficiency practices."


class ReportGenerator:
    def __init__(self, output_pdf_path=None):
        self.output_pdf_path = output_pdf_path

    def create_pdf_report(self, summary_lines, ai_tip, output=None, tip_title="AI Coach advice:"):
        """Write the PDF to `output` (a path or a file-like object) and return it."""
        output = output or self.output_pdf_path
        if isinstance(summary_lines, str):
            summary_lines = [summary_lines]
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except ImportError as error:
            raise Subsystem4Exception("reportlab is not installed.") from error

        c = canvas.Canvas(output, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Smart Energy: Sustainability & Energy Report")

        c.setFont("Helvetica", 12)
        y = height - 90
        for line in summary_lines:
            c.drawString(50, y, line)
            y -= 20
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, tip_title)
        c.setFont("Helvetica", 12)
        for part in textwrap.wrap(ai_tip, 85):
            y -= 18
            c.drawString(50, y, part)

        c.save()
        return output
