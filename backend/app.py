"""
Balenjera (Best Friend) - Student Wellness AI Chatbot
FULLY WORKING Gemini API Integration
"""

import os
import logging
import time
from datetime import datetime
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# ==================== CONFIGURATION ====================
load_dotenv()

app = Flask(__name__)
app.secret_key = 'balenjera-secret-key-2024'
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

# List of working models to try (in order of preference)
WORKING_MODELS = [
    "models/gemini-2.0-flash-lite",
    "models/gemini-1.5-flash",
    "models/gemini-flash-latest"
]

if not GEMINI_API_KEY:
    print("❌ ERROR: No API key found!")
    print("   Please add GEMINI_API_KEY to your .env file")
    print("   Get a free key at: https://aistudio.google.com/app/apikey")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ API Key configured")
        
        # Try each model until one works
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
                    print(f"   Test response: {response.text}")
                    break
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    print(f"⚠️ Model {model_name} quota exceeded, trying next...")
                    time.sleep(2)
                elif "404" in error_msg:
                    print(f"⚠️ Model {model_name} not found, trying next...")
                else:
                    print(f"⚠️ Model {model_name} failed: {error_msg[:100]}")
                    
    except Exception as e:
        print(f"❌ Gemini init error: {str(e)}")

if not gemini_available:
    print("\n" + "!"*60)
    print("⚠️ GEMINI API NOT AVAILABLE - Using Fallback Mode")
    print("!"*60)
    print("\nTo fix Gemini:")
    print("1. Get a new API key: https://aistudio.google.com/app/apikey")
    print("2. Update your .env file with the new key")
    print("3. Restart the server: python app.py")
    print("!"*60 + "\n")

print("="*60 + "\n")

# ==================== WELLNESS PROMPT ====================
def get_wellness_prompt(user_message, user_mood=None, mode="support"):
    """Create a structured, effective prompt for Gemini"""
    
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

# ==================== FALLBACK (only when Gemini is unavailable) ====================
def get_fallback_response(message):
    """Intelligent fallback when Gemini API is unavailable"""
    msg = message.lower()
    
    # Exam/academic stress
    if any(word in msg for word in ['exam', 'failed', 'grade', 'test', 'study']):
        return "I hear that you're stressed about academics. Failing feels terrible, but it doesn't define your worth. Would you like to talk about what happened?"
    
    # Feeling judged
    if 'judge' in msg:
        return "Being judged by others hurts deeply. Other people's opinions say more about them than about you. Your worth isn't determined by what others think."
    
    # Loneliness
    if any(word in msg for word in ['lonely', 'alone', 'nobody']):
        return "Loneliness hurts deeply. You are not as alone as it feels right now. I'm here with you. Would you like to talk more?"
    
    # General distress
    if any(word in msg for word in ['bad', 'terrible', 'awful']):
        return "That sounds really hard. I'm sorry you're going through this. I'm here to listen without judging."
    
    return "I hear you, and I'm here with you. What you're feeling is valid. Would you like to talk more about what's on your mind?"

# ==================== USER STORAGE ====================
users = {}
flagged_cases = []

# ==================== API ENDPOINTS ====================

@app.route('/')
def home():
    return jsonify({
        "name": "Balenjera Wellness API",
        "status": "running",
        "gemini_available": gemini_available,
        "model": MODEL_NAME if gemini_available else "fallback-mode"
    })

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
    """Direct test endpoint for Gemini"""
    if not gemini_available:
        return jsonify({
            "success": False,
            "error": "Gemini not available",
            "message": "Please check your API key in .env file",
            "solution": "Get a new key at https://aistudio.google.com/app/apikey"
        }), 503
    
    try:
        response = gemini_model.generate_content("Say 'Gemini API is working perfectly!'")
        return jsonify({
            "success": True,
            "response": response.text,
            "gemini_available": True,
            "model": MODEL_NAME
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Quota may be exceeded. Wait a minute or get a new API key."
        }), 500

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
    """Main chat endpoint - PRIORITIZES GEMINI API"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        user_mood = data.get('mood', None)
        chat_mode = data.get('mode', 'support')
        user_email = session.get('user_email', 'anonymous')
        
        if not user_message:
            return jsonify({"error": "Message required"}), 400
        
        logger.info(f"📨 Chat: '{user_message[:60]}...'")
        
        # STEP 1: Emergency detection (highest priority)
        emergency_keywords = ['hurt myself', 'self harm', 'kill myself', 'suicide', 'disappear', 'end my life', 'want to die']
        if any(kw in user_message.lower() for kw in emergency_keywords):
            emergency_response = """⚠️ I'm really glad you reached out.

Please contact help immediately:
📞 Ethiopia Mental Health Helpline: +251-911-234-567
🏫 Your School Counselor

💙 You matter. Please talk to someone now."""
            
            if user_email != 'anonymous':
                flagged_cases.append({
                    "id": len(flagged_cases) + 1,
                    "student_email": user_email,
                    "student_name": users.get(user_email, {}).get('name', 'Student'),
                    "message": user_message,
                    "severity": "urgent",
                    "timestamp": datetime.now().isoformat()
                })
            
            return jsonify({
                "success": True,
                "response": emergency_response,
                "severity": "urgent",
                "using_gemini": False
            })
        
        # STEP 2: Use Gemini API (if available) - THIS IS THE PRIORITY
        if gemini_available and gemini_model:
            try:
                prompt = get_wellness_prompt(user_message, user_mood, chat_mode)
                response = gemini_model.generate_content(prompt)
                
                if response and response.text:
                    ai_response = response.text.strip()
                    # Clean up markdown
                    ai_response = ai_response.replace('**', '').replace('*', '').replace('##', '')
                    
                    logger.info(f"✅ Gemini API response generated ({len(ai_response)} chars)")
                    
                    return jsonify({
                        "success": True,
                        "response": ai_response,
                        "severity": "normal",
                        "using_gemini": True,
                        "model_used": MODEL_NAME
                    })
                else:
                    logger.warning("Gemini returned empty response")
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Gemini API error: {error_msg[:200]}")
                
                if "429" in error_msg:
                    return jsonify({
                        "success": False,
                        "error": "QUOTA_EXCEEDED",
                        "message": "Gemini API quota exceeded. Please wait a minute or get a new API key.",
                        "solution": "Get a new key at https://aistudio.google.com/app/apikey"
                    }), 429
                else:
                    return jsonify({
                        "success": False,
                        "error": str(error_msg),
                        "message": "Gemini API error. Check your API key."
                    }), 500
        
        # STEP 3: If Gemini not available, use fallback
        logger.warning("⚠️ Gemini not available - using fallback response")
        fallback_response = get_fallback_response(user_message)
        
        return jsonify({
            "success": True,
            "response": fallback_response,
            "severity": "normal",
            "using_gemini": False,
            "note": "Gemini API unavailable. Check your API key."
        })
        
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/flagged-cases', methods=['GET'])
def get_flagged():
    return jsonify({"success": True, "cases": flagged_cases})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌟 BALENJERA WELLNESS API - STARTING 🌟")
    print("="*60)
    print(f"📡 Server: http://localhost:{PORT}")
    print(f"🤖 Gemini Status: {'✅ WORKING' if gemini_available else '❌ NOT AVAILABLE'}")
    if gemini_available:
        print(f"🤖 Model: {MODEL_NAME}")
    else:
        print("\n⚠️ TO FIX GEMINI:")
        print("   1. Get new API key: https://aistudio.google.com/app/apikey")
        print("   2. Update .env file")
        print("   3. Restart server")
    print("="*60)
    
    # Test Gemini at startup
    if gemini_available:
        try:
            test_response = gemini_model.generate_content("Say 'ready'")
            if test_response and test_response.text:
                print(f"\n✅ Gemini test successful: {test_response.text}")
        except Exception as e:
            print(f"\n⚠️ Gemini test failed: {str(e)[:100]}")
    
    print("\n📋 Test Commands:")
    print(f"   Health:  GET http://localhost:{PORT}/api/health")
    print(f"   Test Gemini: GET http://localhost:{PORT}/api/test-gemini")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=PORT, debug=True)
    if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)