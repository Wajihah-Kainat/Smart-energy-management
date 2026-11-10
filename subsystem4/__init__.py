import os
from flask import Blueprint, render_template, request, redirect, url_for, send_file
from subsystem4.models import DatabaseManager, AICoachService, ReportGenerator, Subsystem4Exception

# Dynamically set absolute paths relative to __init__.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

subsystem4_bp = Blueprint(
    'subsystem4',
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
    url_prefix='/subsystem4'
)

db_manager = DatabaseManager(os.path.join(BASE_DIR, 'energy_data.db'))
ai_coach = AICoachService()
report_generator = ReportGenerator(os.path.join(BASE_DIR, 'sustainability_report.pdf'))


def get_all_logs():
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, kwh_used, cost FROM energy_logs ORDER BY timestamp DESC;")
            return cursor.fetchall()
    except Exception:
        return []


@subsystem4_bp.route('/', methods=['GET', 'POST'])
def dashboard():
    error = None
    if request.method == 'POST':
        try:
            kwh_used = float(request.form.get('kwh_used', 0))
            cost = float(request.form.get('cost', 0))
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO energy_logs (timestamp, kwh_used, cost) VALUES (datetime('now'), ?, ?);",
                    (kwh_used, cost)
                )
            return redirect(url_for('subsystem4.dashboard'))
        except Exception as e:
            error = f"Error adding log: {str(e)}"

    logs = get_all_logs()
    # Updated 'index.html' to 'dashboard.html' per Arshia's instructions
    return render_template('dashboard.html', logs=logs, error=error)


@subsystem4_bp.route('/delete/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    try:
        db_manager.delete_log(log_id)
    except Exception as e:
        print(f"Error deleting log: {e}")
    return redirect(url_for('subsystem4.dashboard'))


@subsystem4_bp.route('/costs-carbon', methods=['GET'])
def costs_carbon():
    logs = get_all_logs()
    return render_template('costs_carbon.html', logs=logs)


@subsystem4_bp.route('/coach', methods=['GET', 'POST'])
def coach():
    error = None
    ai_tips = []
    
    if request.method == 'POST':
        try:
            logs = get_all_logs()
            latest_kwh = logs[0][2] if logs else 15.0
            raw_tip = ai_coach.generate_coach_tips(latest_kwh)
            ai_tips = [raw_tip] if raw_tip else ["Reduce peak hour energy usage.", "Optimize heating schedules."]
        except Subsystem4Exception:
            error = "AI service is currently unavailable. Please try again later."

    return render_template('coach.html', error=error, ai_tips=ai_tips)


@subsystem4_bp.route('/reports', methods=['GET', 'POST'])
def reports():
    error = None
    logs = get_all_logs()
    
    if request.method == 'POST':
        try:
            building = request.form.get('building', 'Main office')
            period = request.form.get('period', 'Last month')
            
            # Save the new report into SQLite
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO reports (building, period, created_date) VALUES (?, ?, date('now'));",
                    (building, period)
                )
            
            summary_text = f"Building: {building} | Period: {period} | Total entries: {len(logs)}"
            latest_kwh = logs[0][2] if logs else 10.0
            tip = ai_coach.generate_coach_tips(latest_kwh)
            report_generator.create_pdf_report(summary_text, tip)
            
            return redirect(url_for('subsystem4.reports'))
        except Exception as e:
            error = str(e)

    # Fetch saved reports dynamically from database
    saved_reports = []
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, building, period, created_date FROM reports ORDER BY id DESC;")
            saved_reports = cursor.fetchall()
    except Exception:
        pass

    return render_template('reports.html', reports=saved_reports, error=error)


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
