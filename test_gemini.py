import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY is not set in .env")

# Configure Gemini
genai.configure(api_key=api_key)

# Use latest model
model = genai.GenerativeModel("gemini-1.5-flash")

# Test
response = model.generate_content("Hello Gemini! Can you say hi?")
print("✅ Gemini Response:", response.text)
