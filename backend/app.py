"""
Balenjera (Best Friend) - Student Wellness AI Chatbot
Complete working version for Python 3.14+ and Render deployment
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# ==================== CONFIGURATION ====================
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'balenjera-secret-key-2024')
CORS(app, origins='*', supports_credentials=True)

PORT = int(os.getenv('PORT', 5000))
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== GEMINI SETUP ====================
print("\n" + "="*60)
print("🔧 INITIALIZING GEMINI API...")
print("="*60)

gemini_model = None
gemini_available = False
MODEL_NAME = None

# Working models for Python 3.14+
WORKING_MODELS = [
    "models/gemini-2.0-flash-lite",
    "models/gemini-1.5-flash",
    "models/gemini-flash-latest"
]

if not GEMINI_API_KEY:
    print("❌ ERROR: No API key found!")
    print("   Please add GEMINI_API_KEY to Render environment variables")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ API Key configured")
        
        for model_name in WORKING_MODELS:
            try:
                print(f"🎯 Testing model: {model_name}")
                test_model = genai.GenerativeModel(model_name)
                response = test_model.generate_content("Say 'OK'")
                
                if response and response.text:
                    gemini_model = test_model
                    MODEL_NAME = model_name
                    gemini_available = True
                    print(f"✅ Gemini WORKING with model: {MODEL_NAME}")
                    break
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    print(f"⚠️ Model {model_name} quota exceeded, trying next...")
                else:
                    print(f"⚠️ Model {model_name} failed: {error_msg[:100]}")
                    
    except Exception as e:
        print(f"❌ Gemini init error: {str(e)}")

if not gemini_available:
    print("\n⚠️ GEMINI API NOT AVAILABLE - Using Fallback Mode")

print("="*60 + "\n")

# ==================== WELLNESS PROMPT ====================
def get_wellness_prompt(user_message, user_mood=None, mode="support"):
    mood_context = f"The user indicated they are feeling: {user_mood}" if user_mood else ""
    
    prompt = f"""You are Balenjera (meaning "Best Friend" in Amharic), an AI wellness companion for boarding school students.

IMPORTANT RULES:
1. Keep responses SHORT - maximum 2-3 sentences
2. Always validate the person's feelings first
3. Never use toxic positivity like "everything happens for a reason"
4. Be warm, kind, and practical
5. For serious distress: suggest contacting a counselor

{mood_context}
Mode: {mode}

Student says: "{user_message}"

Respond as Balenjera (short, warm, never judging):"""
    
    return prompt

# ==================== FALLBACK RESPONSES ====================
def get_fallback_response(message):
    msg = message.lower()
    
    if any(word in msg for word in ['exam', 'failed', 'grade', 'test', 'study']):
        return "I hear that you're stressed about academics. Failing feels terrible, but it doesn't define your worth. Would you like to talk about what happened?"
    
    if 'judge' in msg:
        return "Being judged by others hurts deeply. Other people's opinions say more about them than about you. Your worth isn't determined by what others think."
    
    if any(word in msg for word in ['lonely', 'alone', 'nobody']):
        return "Loneliness hurts deeply. You are not as alone as it feels right now. I'm here with you. Would you like to talk more?"
    
    return "I hear you, and I'm here with you. What you're feeling is valid. Would you like to talk more about what's on your mind?"

# ==================== USER STORAGE ====================
users = {}
flagged_cases = []

# ==================== API ENDPOINTS ====================

@app.route('/')
def serve_index():
    """Serve the home page"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_frontend(path):
    """Serve all frontend files (HTML, CSS, JS)"""
    frontend_path = os.path.join('../frontend', path)
    if os.path.exists(frontend_path):
        return send_from_directory('../frontend', path)
    else:
        return send_from_directory('../frontend', 'index.html')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "gemini_available": gemini_available,
        "model": MODEL_NAME if gemini_available else None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/test-gemini', methods=['GET'])
def test_gemini():
    if not gemini_available:
        return jsonify({
            "success": False,
            "error": "Gemini not available",
            "message": "Check your API key in Render environment variables"
        }), 503
    
    try:
        response = gemini_model.generate_content("Say 'Gemini API is working perfectly!'")
        return jsonify({
            "success": True,
            "response": response.text,
            "gemini_available": True
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    try:
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
        
        logger.info(f"✅ User registered: {email}")
        return jsonify({
            "success": True,
            "message": "Registration successful",
            "user": {"email": email, "name": name, "role": role}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if email not in users or users[email]['password'] != password:
            return jsonify({"error": "Invalid email or password"}), 401
        
        user = users[email]
        session['user_email'] = email
        
        logger.info(f"✅ User logged in: {email}")
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "email": email,
                "name": user['name'],
                "role": user['role']
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        user_mood = data.get('mood', None)
        chat_mode = data.get('mode', 'support')
        
        if not user_message:
            return jsonify({"error": "Message required"}), 400
        
        logger.info(f"📨 Chat: '{user_message[:60]}...'")
        
        # Emergency detection
        emergency_keywords = ['hurt myself', 'self harm', 'kill myself', 'suicide', 'disappear', 'end my life', 'want to die']
        if any(kw in user_message.lower() for kw in emergency_keywords):
            emergency_response = """⚠️ I'm really glad you reached out.

Please contact help immediately:
📞 Ethiopia Mental Health Helpline: +251-911-234-567
🏫 Your School Counselor

💙 You matter. Please talk to someone now."""
            
            return jsonify({
                "success": True,
                "response": emergency_response,
                "severity": "urgent"
            })
        
        # Try Gemini API
        if gemini_available and gemini_model:
            try:
                prompt = get_wellness_prompt(user_message, user_mood, chat_mode)
                response = gemini_model.generate_content(prompt)
                
                if response and response.text:
                    ai_response = response.text.strip()
                    ai_response = ai_response.replace('**', '').replace('*', '').replace('##', '')
                    
                    logger.info(f"✅ Gemini response generated")
                    return jsonify({
                        "success": True,
                        "response": ai_response,
                        "using_gemini": True
                    })
            except Exception as e:
                logger.warning(f"Gemini error: {str(e)[:100]}")
        
        # Fallback
        logger.info("📝 Using fallback response")
        response = get_fallback_response(user_message)
        
        return jsonify({
            "success": True,
            "response": response,
            "using_gemini": False
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/flagged-cases', methods=['GET'])
def get_flagged():
    return jsonify({"success": True, "cases": flagged_cases})

# ==================== RUN SERVER ====================
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌟 BALENJERA WELLNESS API - STARTING 🌟")
    print("="*60)
    print(f"📡 Server: http://localhost:{PORT}")
    print(f"🤖 Python Version: {os.sys.version}")
    print(f"🤖 Gemini Status: {'✅ WORKING' if gemini_available else '❌ NOT AVAILABLE'}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)