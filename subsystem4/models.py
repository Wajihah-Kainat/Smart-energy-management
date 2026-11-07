import os
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class Subsystem4Exception(Exception):
    """Custom exception class for Subsystem 4 errors."""
    pass


class Subsystem4ErrorHandler:
    """Centralized error handler for Subsystem 4."""
    
    @staticmethod
    def handle_database_error(error):
        error_msg = f"[Database Error]: {str(error)}"
        print(error_msg)
        return error_msg

    @staticmethod
    def handle_ai_error(error):
        error_msg = f"[AI Coach Error]: {str(error)}"
        print(error_msg)
        return error_msg

    @staticmethod
    def handle_report_error(error):
        error_msg = f"[Report Generation Error]: {str(error)}"
        print(error_msg)
        return error_msg


class DatabaseManager:
    """Manages SQLite database connections and energy log operations for Subsystem 4."""

    def __init__(self, db_path="subsystem4/energy_data.db"):
        self._db_path = db_path  # Encapsulated attribute
        self._initialize_database()

    @property
    def db_path(self):
        """Getter for database path encapsulation."""
        return self._db_path

    def get_connection(self):
        """Returns a sqlite3 database connection."""
        try:
            return sqlite3.connect(self._db_path)
        except Exception as e:
            raise Subsystem4Exception(Subsystem4ErrorHandler.handle_database_error(e))

    def _initialize_database(self):
        """Creates the energy_logs table if it doesn't already exist."""
        try:
            dir_name = os.path.dirname(self._db_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS energy_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        kwh_used REAL NOT NULL,
                        cost REAL NOT NULL
                    );
                """)
                conn.commit()
        except Exception as e:
            Subsystem4ErrorHandler.handle_database_error(e)

    def delete_log(self, log_id):
        """F5: Delete a specific energy log entry by ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM energy_logs WHERE id = ?", (log_id,))
                conn.commit()
        except Exception as e:
            raise Subsystem4Exception(Subsystem4ErrorHandler.handle_database_error(e))

    def get_logs_by_period(self, start_date, end_date):
        """F9: Retrieve energy logs filtered by a specific reporting period (date range)."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, timestamp, kwh_used, cost FROM energy_logs WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp DESC;",
                    (start_date, end_date)
                )
                return cursor.fetchall()
        except Exception as e:
            raise Subsystem4Exception(Subsystem4ErrorHandler.handle_database_error(e))


class AICoachService:
    """Generates AI energy-saving tips and advice."""

    def __init__(self, api_key=None):
        self._api_key = api_key or os.getenv("OPENAI_API_KEY", "mock-api-key")

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, key):
        self._api_key = key

    def generate_coach_tips(self, kwh_used):
        """F1: Generate AI energy-saving tips based on consumption levels."""
        try:
            if kwh_used > 25.0:
                return "High energy alert! Consider turning off heavy appliances during peak hours to save on costs."
            elif kwh_used >= 15.0:
                return "Moderate usage detected. Try optimizing your daily routine to reduce energy consumption."
            else:
                return "Great job! Your energy usage is at an optimal and sustainable level."
        except Exception as e:
            raise Subsystem4Exception(Subsystem4ErrorHandler.handle_ai_error(e))


class ReportGenerator:
    """F7 & N8: Generates clean, readable PDF energy reports using ReportLab."""

    def __init__(self, filename="subsystem4/sustainability_report.pdf"):
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    def create_pdf_report(self, summary_text, ai_tip):
        """Creates a downloadable PDF report file."""
        try:
            dir_name = os.path.dirname(self._filename)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            doc = SimpleDocTemplate(self._filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title & Content
            story.append(Paragraph("<b>Subsystem 4: Sustainability & Energy Report</b>", styles['Title']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"<b>Summary:</b> {summary_text}", styles['Normal']))
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"<b>AI Coach Advice:</b> {ai_tip}", styles['Normal']))

            doc.build(story)
            return self._filename
        except Exception as e:
            raise Subsystem4Exception(Subsystem4ErrorHandler.handle_report_error(e))