import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'balenjera-secret-key-2024')
CORS(app, origins='*', supports_credentials=True)

PORT = int(os.getenv('PORT', 5000))
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gemini setup
gemini_available = False
gemini_model = None

print("=" * 50)
print("Starting Balenjera API...")
print("=" * 50)

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel("gemini-2.0-flash-lite")
        gemini_available = True
        print("✅ Gemini API connected successfully")
    except Exception as e:
        print(f"⚠️ Gemini API error: {str(e)}")
else:
    print("⚠️ No API key found")

print("=" * 50)

# Users storage
users = {}
flagged_cases = []

# Frontend routes
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_frontend(path):
    file_path = os.path.join('../frontend', path)
    if os.path.exists(file_path):
        return send_from_directory('../frontend', path)
    return send_from_directory('../frontend', 'index.html')

# API routes
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "gemini_available": gemini_available,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'student')
    
    if not email or not name or not password:
        return jsonify({"error": "All fields required"}), 400
    
    if email in users:
        return jsonify({"error": "Email already registered"}), 400
    
    users[email] = {
        "name": name,
        "password": password,
        "role": role,
        "created_at": datetime.now().isoformat()
    }
    
    return jsonify({
        "success": True,
        "message": "Registration successful",
        "user": {"email": email, "name": name, "role": role}
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if email not in users or users[email]['password'] != password:
        return jsonify({"error": "Invalid email or password"}), 401
    
    session['user_email'] = email
    
    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "email": email,
            "name": users[email]['name'],
            "role": users[email]['role']
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({"error": "Message required"}), 400
    
    # Emergency check
    emergency_words = ['hurt myself', 'self harm', 'kill myself', 'suicide', 'disappear', 'end my life', 'want to die']
    for word in emergency_words:
        if word in user_message.lower():
            return jsonify({
                "success": True,
                "response": "⚠️ I'm really glad you reached out. Please contact Ethiopia Mental Health Helpline: +251-911-234-567 or your school counselor immediately. You matter. 💙",
                "severity": "urgent"
            })
    
    # Try Gemini
    if gemini_available and gemini_model:
        try:
            prompt = f"You are Balenjera, a caring AI friend. Respond briefly (2-3 sentences) to this student: {user_message}"
            response = gemini_model.generate_content(prompt)
            if response and response.text:
                return jsonify({
                    "success": True,
                    "response": response.text,
                    "using_gemini": True
                })
        except Exception as e:
            print(f"Gemini error: {e}")
    
    # Fallback responses
    msg = user_message.lower()
    if 'sad' in msg:
        reply = "I hear that you're feeling sad. That's completely valid. Would you like to talk more about what's bothering you? I'm here to listen. 💙"
    elif 'anxious' in msg or 'stress' in msg:
        reply = "Anxiety can be really uncomfortable. Let's try a deep breath together. Breathe in... 1-2-3-4. Hold... 1-2-3-4. Breathe out... 1-2-3-4. How do you feel now? 🍃"
    elif 'lonely' in msg or 'alone' in msg:
        reply = "Loneliness hurts deeply. You are not as alone as it feels right now. I'm here with you. Would you like to talk more? 🫂"
    elif 'exam' in msg or 'fail' in msg or 'grade' in msg:
        reply = "Academic stress is real. Failing doesn't define your worth. You're doing your best, and that's enough. Want to talk about what happened?"
    else:
        reply = "I hear you, and I'm here with you. What you're feeling is valid. Would you like to tell me more? 💙"
    
    return jsonify({
        "success": True,
        "response": reply,
        "using_gemini": False
    })

@app.route('/api/flagged-cases', methods=['GET'])
def get_flagged():
    return jsonify({"success": True, "cases": flagged_cases})

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🌟 Balenjera API is running!")
    print("=" * 50)
    print(f"Server: http://localhost:{PORT}")
    print(f"Gemini: {'Connected' if gemini_available else 'Fallback mode'}")
    print("=" * 50 + "\n")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)