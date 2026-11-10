import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, send_file
from subsystem4.models import DatabaseManager, AICoachService, ReportGenerator, Subsystem4Exception

# Dynamically set absolute paths relative to app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Define as a Blueprint for integration with the main app
subsystem4_bp = Blueprint(
    'subsystem4',
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
    url_prefix='/subsystem4' # Or can be mounted directly depending on group setup
)

# Initialize Subsystem 4 managers & services
db_manager = DatabaseManager(os.path.join(BASE_DIR, 'energy_data.db'))
ai_coach = AICoachService()
report_generator = ReportGenerator(os.path.join(BASE_DIR, 'sustainability_report.pdf'))


def get_all_logs():
    """Helper to fetch all logs from SQLite."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, kwh_used, cost FROM energy_logs ORDER BY timestamp DESC;")
            return cursor.fetchall()
    except Exception:
        return []


@subsystem4_bp.route('/coach', methods=['GET', 'POST'])
def coach():
    """AI Sustainability Coach page (/coach)"""
    error = None
    ai_tips = []
    
    if request.method == 'POST':
        try:
            building = request.form.get('building', 'Main office')
            period = request.form.get('period', 'Last 30 days')
            
            # Fetch usage summary or latest data to send to OpenAI
            logs = get_all_logs()
            latest_kwh = logs[0][2] if logs else 15.0
            
            # Generate tips with fallback handling if AI service is unavailable
            raw_tip = ai_coach.generate_coach_tips(latest_kwh)
            # Split into individual tips if it's a block of text
            ai_tips = [raw_tip] if raw_tip else ["Reduce peak hour energy usage.", "Optimize heating schedules.", "Inspect device efficiency."]
        except Subsystem4Exception as e:
            error = "AI service is currently unavailable. Please try again later."

    return render_template('coach.html', error=error, ai_tips=ai_tips)


@subsystem4_bp.route('/reports', methods=['GET', 'POST'])
def reports():
    """Reports creation and view page (/reports)"""
    error = None
    logs = get_all_logs()
    
    if request.method == 'POST':
        try:
            building = request.form.get('building', 'Main office')
            period = request.form.get('period', 'Last month')
            
            summary_text = f"Building: {building} | Period: {period} | Total entries: {len(logs)}"
            latest_kwh = logs[0][2] if logs else 10.0
            tip = ai_coach.generate_coach_tips(latest_kwh)
            
            report_generator.create_pdf_report(summary_text, tip)
        except Exception as e:
            error = str(e)

    return render_template('reports.html', logs=logs, error=error)


@subsystem4_bp.route('/report/pdf', methods=['GET'])
def download_pdf_report():
    logs = get_all_logs()
    summary_text = f"Total logged entries: {len(logs)}"
    latest_kwh = logs[0][2] if logs else 10.0
    tip = ai_coach.generate_coach_tips(latest_kwh)
    
    pdf_path = report_generator.create_pdf_report(summary_text, tip)
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name='energy_report.pdf',
        mimetype='application/pdf'
    )