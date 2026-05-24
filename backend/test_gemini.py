import google.generativeai as genai

API_KEY = "AIzaSyCUJFAIxmXY8svLyPWV39Fg0fMi7TmGSJY"

print("Testing Gemini API...")
genai.configure(api_key=API_KEY)

# List available models
print("\nAvailable models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  {m.name}")

# Test with correct model
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Say 'Hello! I am working!'")
print(f"\nResponse: {response.text}")
print("\n✅ Gemini is WORKING!")