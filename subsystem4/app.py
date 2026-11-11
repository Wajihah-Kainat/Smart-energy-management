import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file
from subsystem4.models import DatabaseManager, AICoachService, ReportGenerator, Subsystem4Exception

# Dynamically set absolute paths relative to app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
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


@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    ai_tip = None
    if request.method == 'POST':
        try:
            kwh_used = float(request.form.get('kwh_used', 0))
            cost = float(request.form.get('cost', kwh_used * 0.30)) # default cost estimation
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO energy_logs (timestamp, kwh_used, cost) VALUES (?, ?, ?);",
                    (timestamp, kwh_used, cost)
                )
                conn.commit()

            ai_tip = ai_coach.generate_coach_tips(kwh_used)
            return redirect(url_for('index'))
        except (ValueError, Subsystem4Exception) as e:
            error = str(e)

    logs = get_all_logs()
    return render_template('index.html', logs=logs, error=error, ai_tip=ai_tip)


@app.route('/delete/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    try:
        db_manager.delete_log(log_id)
    except Subsystem4Exception:
        pass
    return redirect(url_for('index'))


@app.route('/filter', methods=['GET'])
def filter_logs():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date and end_date:
        logs = db_manager.get_logs_by_period(start_date, end_date)
    else:
        logs = get_all_logs()
        
    return render_template('index.html', logs=logs, start_date=start_date, end_date=end_date)


@app.route('/report/pdf', methods=['GET'])
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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', logs=get_all_logs(), error="Page not found"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('index.html', logs=get_all_logs(), error="Internal server error"), 500


if __name__ == '__main__':
    app.run(debug=True)