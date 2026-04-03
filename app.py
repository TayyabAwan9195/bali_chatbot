import os
from flask import Flask, request, render_template, jsonify, redirect, url_for
from datetime import datetime
import sqlite3
import json
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from core.chatbot import bot

app = Flask(__name__, template_folder='templates')

# Database helper (supports env var override for hosting)
DB_FILE = os.getenv('DATABASE_FILE', 'leads.db')

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def _normalize_whatsapp_number(number: str) -> str:
    if not number:
        return ''
    return number if number.startswith('whatsapp:') else f'whatsapp:{number}'


def _get_twilio_client() -> Client:
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        raise RuntimeError('TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in environment variables')
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_whatsapp_message(to_number: str, message: str) -> str:
    if not to_number or not message:
        raise ValueError('Recipient number and message are required')

    from_whatsapp = _normalize_whatsapp_number(TWILIO_WHATSAPP_NUMBER)
    to_whatsapp = _normalize_whatsapp_number(to_number)

    if not from_whatsapp:
        raise RuntimeError('TWILIO_WHATSAPP_NUMBER must be set in environment variables')

    client = _get_twilio_client()
    twilio_message = client.messages.create(
        body=message,
        from_=from_whatsapp,
        to=to_whatsapp,
    )
    return twilio_message.sid


@app.route('/')
def home():
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bali Legal Partner - Business Setup & Legal Services</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="{url_for('static', filename='css/base.css')}" rel="stylesheet">
    <style>
        .hero-section {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 80px 0;
            text-align: center;
        }}
        .hero-section h1 {{
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }}
        .hero-section p {{
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }}
        .features-section {{
            padding: 60px 0;
            background-color: #f8f9fa;
        }}
        .feature-card {{
            background: white;
            border-radius: var(--border-radius);
            padding: 30px;
            text-align: center;
            box-shadow: var(--shadow);
            transition: transform 0.3s ease;
            height: 100%;
        }}
        .feature-card:hover {{
            transform: translateY(-5px);
        }}
        .feature-card i {{
            font-size: 3rem;
            color: var(--primary);
            margin-bottom: 1rem;
        }}
        .feature-card h3 {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }}
        .cta-section {{
            background-color: var(--sidebar-bg);
            color: white;
            padding: 60px 0;
            text-align: center;
        }}
        .cta-button {{
            display: inline-block;
            padding: 15px 30px;
            background-color: var(--primary);
            color: white;
            text-decoration: none;
            border-radius: var(--border-radius);
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            margin: 10px;
        }}
        .cta-button:hover {{
            background-color: var(--primary-dark);
            transform: translateY(-2px);
            color: white;
        }}
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            background-color: #28a745;
            border-radius: 50%;
            margin-left: 8px;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="title">
            <i class="fas fa-balance-scale"></i>
            Bali Legal Partner
        </div>
        <div class="user-info">
            <span>System Online</span>
            <div class="status-indicator"></div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
        <div class="container">
            <h1>Welcome to Bali Legal Partner</h1>
            <p>Your trusted partner for business setup, legal services, and company registration in Indonesia</p>
            <div>
                <a href="{url_for('chat')}" class="cta-button">
                    <i class="fas fa-comments"></i> Try Chat Interface
                </a>
                <a href="{url_for('admin_dashboard')}" class="cta-button">
                    <i class="fas fa-tachometer-alt"></i> Admin Dashboard
                </a>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
        <div class="container">
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="feature-card">
                        <i class="fas fa-building"></i>
                        <h3>Company Setup</h3>
                        <p>Complete business registration and incorporation services for foreign investors in Bali and Indonesia.</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-card">
                        <i class="fas fa-file-contract"></i>
                        <h3>Legal Services</h3>
                        <p>Comprehensive legal support including licensing, permits, tax compliance, and business advisory.</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-card">
                        <i class="fas fa-comments"></i>
                        <h3>AI Assistant</h3>
                        <p>24/7 intelligent chatbot to answer your questions about business setup, visas, and legal requirements.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
        <div class="container">
            <h2>Ready to Start Your Business Journey?</h2>
            <p>Chat with our AI assistant or access the admin dashboard to manage leads and communications.</p>
            <div>
                <a href="{url_for('chat')}" class="cta-button">
                    <i class="fas fa-robot"></i> Chat with AI Assistant
                </a>
                <a href="{url_for('admin_dashboard')}" class="cta-button">
                    <i class="fas fa-cog"></i> Admin Panel
                </a>
                <a href="{url_for('test_chat')}" class="cta-button">
                    <i class="fas fa-flask"></i> Testing Mode
                </a>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer style="background-color: #343a40; color: white; text-align: center; padding: 20px;">
        <div class="container">
            <p>&copy; 2024 Bali Legal Partner. All rights reserved.</p>
            <p>Professional legal and business setup services in Indonesia.</p>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/favicon.ico')
def favicon():
    return ('', 204)

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    try:
        # 1️⃣ Get incoming message and sender
        body = request.form.get('Body', '').strip()
        sender = request.form.get('From', '').strip()
        print(f"[WhatsApp] Incoming message from {sender}: {body}")

        # 2️⃣ Validate input
        if not body:
            print("[WhatsApp] No message body received")
            return "", 400

        # 3️⃣ Get bot response
        reply_text = bot.get_response(user_id=sender or 'unknown', message=body)
        print(f"[Bot Reply] Response from bot: {reply_text!r}")

        # 4️⃣ Check for empty reply
        if not reply_text:
            print("[WhatsApp] Bot returned empty response")
            reply_text = "🤖 Sorry, I couldn't process your message."

        # 5️⃣ Create Twilio response
        response = MessagingResponse()
        response.message(reply_text)
        print("[WhatsApp] Reply sent successfully")

        return str(response), 200, {'Content-Type': 'application/xml'}

    except Exception as e:
        print(f"[WhatsApp] Error handling message: {e}")
        return "Internal Server Error", 500

# simple web UI for manual testing with conversation history
# chat_history = []  # list of (question, answer)
# Removed /ui route - using /chat as main interface
chat_history = {}  # {user_id: [messages]}

# Admin Dashboard
@app.route('/admin')
def admin_dashboard():
    conn = get_db_connection()
    leads_raw = conn.execute('SELECT * FROM leads').fetchall()
    conn.close()
    # Parse JSON fields
    leads = []
    for lead_row in leads_raw:
        lead = dict(lead_row)
        lead['lead_info'] = json.loads(lead['lead_info'])
        lead['qualification'] = json.loads(lead['qualification'])
        lead['history'] = json.loads(lead['history'])
        leads.append(lead)
    return render_template('admin_dashboard.html', leads=leads)

# Lead Details
@app.route('/lead/<user_id>')
def lead_detail(user_id):
    conn = get_db_connection()
    lead = conn.execute('SELECT * FROM leads WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    if lead:
        lead = dict(lead)
        lead['history'] = json.loads(lead['history'])
        lead['lead_info'] = json.loads(lead['lead_info'])
        lead['qualification'] = json.loads(lead['qualification'])
        return render_template('lead_detail.html', lead=lead)
    return "Lead not found", 404

# Send Message from Admin
@app.route('/admin/send_message', methods=['POST'])
def send_message():
    user_id = request.form.get('user_id')
    message = request.form.get('message')
    if user_id and message:
        try:
            send_whatsapp_message(user_id, message)
        except Exception as e:
            print(f"[Twilio] Failed to send WhatsApp message to {user_id}: {e}")
            return str(e), 500
        return redirect(url_for('lead_detail', user_id=user_id))
    return "Error", 400

# Test Chat Mode
# This route is used by the web UI (and the JS frontend) for interactive testing.
test_chat_history = {}  # {phone: [messages]}

@app.route('/test_chat', methods=['GET', 'POST'])
def test_chat():
    if request.method == 'POST':
        data = request.get_json()
        message = data.get('message', '')
        phone = data.get('phone', 'web')
        if message:
            # Get bot response
            response = bot.get_response(user_id=phone, message=message)
            # Store in history
            if phone not in test_chat_history:
                test_chat_history[phone] = []
            test_chat_history[phone].append({'type': 'user', 'text': message})
            test_chat_history[phone].append({'type': 'bot', 'text': response})
            # Keep last 50
            if len(test_chat_history[phone]) > 50:
                test_chat_history[phone] = test_chat_history[phone][-50:]
            return jsonify({'response': response})
    phone = request.args.get('phone', 'web')
    history = test_chat_history.get(phone, [])
    return render_template('test_chat.html', phone=phone, chat_history=history)

@app.route('/chat', methods=['GET'])
def chat():
    # Keep this as a simple landing page for the chat UI (redirects to test_chat)
    return redirect(url_for('test_chat'))

# API Endpoints
@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    user_id = data.get('user_id', 'api')
    message = data.get('message', '')
    if message:
        response = bot.get_response(user_id=user_id, message=message)
        return jsonify({'response': response})
    return jsonify({'error': 'No message provided'}), 400

@app.route('/leads', methods=['GET'])
def leads_api():
    conn = get_db_connection()
    leads = conn.execute('SELECT user_id, lead_info, pending_flow, lead_category, last_interaction FROM leads').fetchall()
    conn.close()
    leads_list = []
    for lead in leads:
        lead_dict = dict(lead)
        lead_dict['lead_info'] = json.loads(lead_dict['lead_info'])
        leads_list.append(lead_dict)
    return jsonify(leads_list)

@app.route('/lead/<user_id>', methods=['GET'])
def lead_api(user_id):
    conn = get_db_connection()
    lead = conn.execute('SELECT * FROM leads WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    if lead:
        lead_dict = dict(lead)
        lead_dict['history'] = json.loads(lead_dict['history'])
        lead_dict['lead_info'] = json.loads(lead_dict['lead_info'])
        lead_dict['qualification'] = json.loads(lead_dict['qualification'])
        return jsonify(lead_dict)
    return jsonify({'error': 'Lead not found'}), 404

# error handlers to avoid crash pages
@app.errorhandler(500)
def server_error(e):
    return "An internal error occurred. Please try again later.", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask app on http://0.0.0.0:{port} ...")
    app.run(host="0.0.0.0", port=port, debug=False)
