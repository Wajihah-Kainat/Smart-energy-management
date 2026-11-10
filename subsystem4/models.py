import os
import sqlite3

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Energy logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS energy_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    kwh_used REAL NOT NULL,
                    cost REAL NOT NULL
                );
            ''')
            # Reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    building TEXT NOT NULL,
                    period TEXT NOT NULL,
                    created_date TEXT NOT NULL
                );
            ''')
            conn.commit()

    def delete_log(self, log_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM energy_logs WHERE id = ?;", (log_id,))
            conn.commit()


class AICoachService:
    def __init__(self):
        self.client = OpenAI() if (OpenAI and os.environ.get("OPENAI_API_KEY")) else None

    def generate_coach_tips(self, latest_kwh):
        if not self.client:
            if latest_kwh > 20:
                return "Energy usage is high. Consider shifting heavy appliance usage to off-peak hours."
            return "Great job! Your energy usage is at an optimal and sustainable level."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI sustainability coach for an energy management system. Provide 1 brief, practical tip."},
                    {"role": "user", "content": f"Latest energy usage is {latest_kwh} kWh. Give a short saving tip."}
                ],
                max_tokens=60
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "AI service is currently unavailable. Please maintain current efficiency practices."


class ReportGenerator:
    def __init__(self, output_pdf_path):
        self.output_pdf_path = output_pdf_path

    def create_pdf_report(self, summary_text, ai_tip):
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            c = canvas.Canvas(self.output_pdf_path, pagesize=letter)
            width, height = letter

            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Subsystem 4: Sustainability & Energy Report")

            c.setFont("Helvetica", 12)
            c.drawString(50, height - 90, f"Summary: {summary_text}")
            c.drawString(50, height - 120, f"AI Coach Advice: {ai_tip}")

            c.save()
            return self.output_pdf_path
        except ImportError:
            with open(self.output_pdf_path.replace('.pdf', '.txt'), 'w') as f:
                f.write(f"Report Summary: {summary_text}\nAI Advice: {ai_tip}")
            return self.output_pdf_path


class Subsystem4Exception(Exception):
    pass