import os
from flask import Flask, request, render_template, jsonify, redirect, url_for
from datetime import datetime
import sqlite3
import json

from core.chatbot import bot

app = Flask(__name__, template_folder='templates')

# Database helper (supports env var override for hosting)
DB_FILE = os.getenv('DATABASE_FILE', 'leads.db')

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

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
                <a href="{url_for('ui')}" class="cta-button">
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
                <a href="{url_for('ui')}" class="cta-button">
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

# simple web UI for manual testing with conversation history
# chat_history = []  # list of (question, answer)
chat_history = []  # list of {'type': 'user' or 'bot', 'text': str, 'time': str}

@app.route('/ui', methods=['GET', 'POST'])
def ui():
    global chat_history
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if question:
            # Add user message
            chat_history.append({
                'type': 'user',
                'text': question,
                'time': datetime.now().strftime('%H:%M')
            })
            # Get bot response
            response = bot.get_response(user_id="web", message=question)
            print(f"DEBUG: User question: {question}")
            print(f"DEBUG: Bot response: {response}")
            # Add bot message
            chat_history.append({
                'type': 'bot',
                'text': response,
                'time': datetime.now().strftime('%H:%M')
            })
            # Keep last 50 messages
            if len(chat_history) > 50:
                chat_history = chat_history[-50:]

    # Build chat HTML
    chat_html = ''
    for msg in chat_history:
        if msg['type'] == 'user':
            chat_html += f'<div class="message user"><div class="bubble">{msg["text"]}</div><div class="time">{msg["time"]}</div></div>'
        else:
            chat_html += f'<div class="message bot"><div class="bubble">{msg["text"]}</div><div class="time">{msg["time"]}</div></div>'

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bali Legal Partner Chatbot</title>
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #e5ddd5;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}
        .header {{
            background-color: #075e54;
            color: white;
            padding: 10px 20px;
            text-align: center;
            font-size: 1.2em;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .chat-container {{
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .message {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            margin-bottom: 10px;
        }}
        .message.user {{
            align-items: flex-end;
        }}
        .bubble {{
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
            position: relative;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            font-size: 0.95em;
            line-height: 1.4;
        }}
        .message.bot .bubble {{
            background-color: #343a40;
            color: #ffffff;
            border: 1px solid #495057;
        }}
        .message.user .bubble {{
            background-color: #25d366;
            color: #ffffff;
        }}
        .time {{
            font-size: 0.7em;
            color: #999;
            margin-top: 4px;
            font-weight: 400;
        }}
        .message.user .time {{
            text-align: right;
        }}
        .input-container {{
            background-color: #f0f0f0;
            padding: 10px;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
            align-items: center;
            box-shadow: 0 -2px 4px rgba(0,0,0,0.1);
        }}
        .input-container input {{
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ccc;
            border-radius: 25px;
            outline: none;
            font-size: 1em;
            background-color: #ffffff;
        }}
        .input-container input:focus {{
            border-color: #25d366;
        }}
        .input-container button {{
            padding: 12px 24px;
            background-color: #25d366;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 500;
            transition: background-color 0.2s;
        }}
        .input-container button:hover {{
            background-color: #128c7e;
        }}
        .input-container button:active {{
            transform: scale(0.98);
        }}
        @media (max-width: 600px) {{
            .bubble {{
                max-width: 85%;
            }}
            .header {{
                font-size: 1em;
                padding: 8px 15px;
            }}
        }}
        .typing {{
            display: none;
            font-style: italic;
            color: #999;
            padding: 10px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        Bali Legal Partner Chatbot
    </div>
    <div class="chat-container" id="chat-container">
        {chat_html}
        <div class="typing" id="typing-indicator">Bot is typing...</div>
    </div>
    <form class="input-container" method="post" id="chat-form">
        <input type="text" name="question" placeholder="Type a message..." required id="message-input">
        <button type="submit">Send</button>
    </form>
    <script>
        // Scroll to bottom on load
        const chatContainer = document.getElementById('chat-container');
        function scrollToBottom() {{
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }}
        scrollToBottom();

        // Auto-submit on Enter
        document.getElementById('message-input').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                e.preventDefault();
                this.form.submit();
            }}
        }});

        // Show typing indicator on form submit
        document.getElementById('chat-form').addEventListener('submit', function() {{
            document.getElementById('typing-indicator').style.display = 'block';
            scrollToBottom();
        }});
    </script>
</body>
</html>
    """

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
        from core.chatbot import send_whatsapp_message
        send_whatsapp_message(user_id, message)
        return redirect(url_for('lead_detail', user_id=user_id))
    return "Error", 400

# Test Chat Mode
test_chat_history = {}  # {phone: [messages]}

@app.route('/test_chat', methods=['GET', 'POST'])
def test_chat():
    phone = request.args.get('phone', '')
    if request.method == 'POST':
        data = request.get_json()
        phone = data.get('phone', '')
        message = data.get('message', '')
        if phone and message:
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
    history = test_chat_history.get(phone, [])
    return render_template('test_chat.html', phone=phone, chat_history=history)

# API Endpoints
@app.route('/chat', methods=['POST'])
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
