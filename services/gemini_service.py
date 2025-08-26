import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is not set in .env")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_gemini_response(few_shot_prompt: str) -> str:
    """
    Call Gemini AI with the given prompt and return the response text.
    """
    response = model.generate_content(contents=[few_shot_prompt])
    return response.text.strip()
