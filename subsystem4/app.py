from flask import Blueprint, render_template, request, send_file
import os
import sqlite3

# Define the Blueprint for Subsystem 4
subsystem4_bp = Blueprint('subsystem4', __name__, template_folder='templates')

@subsystem4_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@subsystem4_bp.route('/costs-carbon')
def costs_carbon():
    return render_template('costs_carbon.html')

@subsystem4_bp.route('/reports')
def reports():
    return render_template('reports.html')

@subsystem4_bp.route('/reports/download', methods=['GET'])
def download_pdf_report():
    # Serve the generated sustainability PDF report if available
    pdf_path = os.path.join(os.path.dirname(__file__), 'sustainability_report.pdf')
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    return "PDF report not found", 404

@subsystem4_bp.route('/coach', methods=['GET', 'POST'])
def coach():
    ai_tips = None
    error = None
    
    if request.method == 'POST':
        building = request.form.get('building')
        period = request.form.get('period')
        
        try:
            # Generate AI sustainability tips based on selected inputs
            ai_tips = [
                f"Optimize HVAC scheduling for your {building} during the {period}.",
                "Inspect insulation around doors and windows to reduce heating/cooling loss.",
                "Switch to LED lighting fixtures across all common areas to lower baseline draw."
            ]
        except Exception as e:
            error = f"Could not generate AI tips at this moment: {str(e)}"
            
    return render_template('coach.html', ai_tips=ai_tips, error=error)