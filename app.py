import os
import sqlite3
from flask import Flask, request, send_file
from dotenv import load_dotenv
import openai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

load_dotenv()
app = Flask(__name__)

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('energy_app.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return '''
        <div style='font-family: Arial; padding: 30px;'>
            <h2>Subsystem 4: AI Sustainability Coach & Reports 🚀</h2>
            <p><a href='/test-coach'>👉 Go to AI Energy Coach</a></p>
            <p><a href='/generate-pdf-report'>👉 Download PDF Sustainability Report</a></p>
        </div>
    '''

@app.route('/test-coach', methods=['GET', 'POST'])
def test_coach():
    advice = "Click the button below to get an energy-saving tip!"
    if request.method == 'POST':
        try:
            # Try using OpenAI if keys/credits are available
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': 'You are an AI sustainability coach. Give 1 short, practical energy-saving tip for a building.'},
                    {'role': 'user', 'content': 'Give me an energy tip.'}
                ]
            )
            advice = response.choices[0].message.content
        except Exception as e:
            # FREE FALLBACK: If billing/auth fails, provide a smart mock tip so the app works seamlessly!
            import random
            fallback_tips = [
                "💡 [Smart Coach Fallback] Optimize your HVAC schedule to turn off 1 hour before office closing time.",
                "💡 [Smart Coach Fallback] Upgrade remaining hallway fixtures to motion-sensor LED lighting.",
                "💡 [Smart Coach Fallback] Seal exterior windows and doors to reduce HVAC thermal loss by up to 15%.",
                "💡 [Smart Coach Fallback] Set smart thermostats 2 degrees higher during summer peak cooling hours."
            ]
            advice = random.choice(fallback_tips)
            
        # Save tip to SQLite database
        try:
            conn = sqlite3.connect('energy_app.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO recommendations (user_id, text) VALUES (?, ?)', (1, advice))
            conn.commit()
            conn.close()
        except Exception as db_err:
            print(f"DB Error: {db_err}")

    return f'''
        <div style='font-family: Arial; padding: 30px;'>
            <h2>🤖 AI Sustainability Coach (Subsystem 4)</h2>
            <p><b>Advice:</b> {advice}</p>
            <form method='POST'>
                <button type='submit' style='padding: 10px 20px; font-size: 16px;'>Generate AI Tip</button>
            </form>
            <br><a href='/'>Back Home</a>
        </div>
    '''

@app.route('/generate-pdf-report')
def generate_pdf_report():
    # Create PDF in memory using ReportLab
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Title & Header
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, 750, "Energy Sustainability Report")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, 730, "Subsystem 4: AI Coach & Automated Reports")
    p.line(50, 720, 560, 720)
    
    # Fetch recent recommendations from SQLite
    conn = sqlite3.connect('energy_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT text, created_at FROM recommendations ORDER BY id DESC LIMIT 5')
    rows = cursor.fetchall()
    conn.close()
    
    # Write recommendations into the PDF
    y = 680
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Recent Recommendations Log:")
    y -= 30
    
    p.setFont("Helvetica", 11)
    if not rows:
        p.drawString(50, y, "No tips generated yet! Go to /test-coach to make some.")
    else:
        for row in rows:
            tip_text = f"• [{row[1]}] {row[0]}"
            p.drawString(50, y, tip_text[:90])
            y -= 25
            
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="sustainability_report.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)