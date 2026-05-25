import google.generativeai as genai

# Replace with YOUR actual new API key
genai.configure(api_key="AIzaSyBR4V021mUaaCSjfRwJ5D4xwt8reS2P0Cs")

model = genai.GenerativeModel("gemini-2.0-flash-lite")
response = model.generate_content("What is the most common human feeling?")

print("=" * 50)
print("GEMINI API TEST")
print("=" * 50)
print(response.text)
print("=" * 50)