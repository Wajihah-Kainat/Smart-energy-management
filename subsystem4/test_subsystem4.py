import unittest
import os
from subsystem4.models import (
    DatabaseManager, 
    AICoachService, 
    ReportGenerator, 
    Subsystem4ErrorHandler, 
    Subsystem4Exception
)

class Subsystem4ModelTests(unittest.TestCase):
    """15 comprehensive unit tests specifically for Subsystem 4."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_db = "test_subsystem4.db"
        self.db_manager = DatabaseManager(self.test_db)
        self.ai_coach = AICoachService()
        self.report_gen = ReportGenerator("test_report.pdf")

    def tearDown(self):
        """Clean up generated test files after each test."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        if os.path.exists("test_report.pdf"):
            os.remove("test_report.pdf")
        if os.path.exists("sustainability_report.pdf"):
            os.remove("sustainability_report.pdf")

    # --- DatabaseManager Tests (1-5) ---
    def test_1_db_path_getter(self):
        """Test DatabaseManager db_path getter encapsulation."""
        self.assertEqual(self.db_manager.db_path, self.test_db)

    def test_2_get_connection(self):
        """Test that get_connection returns a valid sqlite3 connection."""
        conn = self.db_manager.get_connection()
        self.assertIsNotNone(conn)
        conn.close()

    def test_3_initialize_database(self):
        """Test that the energy_logs table is created correctly."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='energy_logs';")
            self.assertIsNotNone(cursor.fetchone())

    def test_4_insert_energy_log(self):
        """Test inserting an energy log entry into the database."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO energy_logs (timestamp, kwh_used, cost) VALUES (?, ?, ?)", 
                           ("2026-11-05 12:00:00", 22.5, 3.38))
            conn.commit()
            cursor.execute("SELECT COUNT(*) FROM energy_logs;")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)

    def test_5_query_energy_log(self):
        """Test querying inserted energy data."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO energy_logs (timestamp, kwh_used, cost) VALUES (?, ?, ?)", 
                           ("2026-11-05 12:00:00", 12.0, 1.80))
            conn.commit()
            cursor.execute("SELECT kwh_used FROM energy_logs;")
            val = cursor.fetchone()[0]
            self.assertEqual(val, 12.0)

    # --- AICoachService Tests (6-9) ---
    def test_6_ai_coach_high_usage(self):
        """Test AI coach feedback for high energy consumption (>25 kWh)."""
        tip = self.ai_coach.generate_coach_tips(30.0)
        self.assertIn("High energy alert", tip)

    def test_7_ai_coach_moderate_usage(self):
        """Test AI coach feedback for moderate energy consumption (15-25 kWh)."""
        tip = self.ai_coach.generate_coach_tips(18.0)
        self.assertIn("Moderate usage detected", tip)

    def test_8_ai_coach_low_usage(self):
        """Test AI coach feedback for optimal/low energy consumption (<15 kWh)."""
        tip = self.ai_coach.generate_coach_tips(10.0)
        self.assertIn("Great job", tip)

    def test_9_ai_coach_api_key_encapsulation(self):
        """Test getter and setter encapsulation for the AI coach API key."""
        self.ai_coach.api_key = "subsystem4-secret-key"
        self.assertEqual(self.ai_coach.api_key, "subsystem4-secret-key")

    # --- ReportGenerator Tests (10-11) ---
    def test_10_report_filename_getter(self):
        """Test ReportGenerator filename property getter."""
        self.assertEqual(self.report_gen.filename, "test_report.pdf")

    def test_11_create_pdf_report(self):
        """Test that ReportGenerator creates a physical PDF report file."""
        filename = self.report_gen.create_pdf_report("Summary Data", "Sample Tip")
        self.assertTrue(os.path.exists(filename))

    # --- Exception Handling & Error Handler Tests (12-15) ---
    def test_12_subsystem4_exception(self):
        """Test raising and catching the custom Subsystem4Exception."""
        with self.assertRaises(Subsystem4Exception):
            raise Subsystem4Exception("Subsystem 4 failure simulated")

    def test_13_error_handler_database(self):
        """Test Subsystem4ErrorHandler handling database errors."""
        msg = Subsystem4ErrorHandler.handle_database_error(Exception("DB connection error"))
        self.assertIn("[Database Error]", msg)

    def test_14_error_handler_ai(self):
        """Test Subsystem4ErrorHandler handling AI coach errors."""
        msg = Subsystem4ErrorHandler.handle_ai_error(Exception("AI service unavailable"))
        self.assertIn("[AI Coach Error]", msg)

    def test_15_error_handler_report(self):
        """Test Subsystem4ErrorHandler handling report generation errors."""
        msg = Subsystem4ErrorHandler.handle_report_error(Exception("PDF layout error"))
        self.assertIn("[Report Generation Error]", msg)

if __name__ == "__main__":
    unittest.main()