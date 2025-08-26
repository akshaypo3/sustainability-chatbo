from fastapi import FastAPI, HTTPException, Query
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Gemini AI setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is not set in .env")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = FastAPI()

# Root endpoint
@app.get("/")
def root():
    return {"message": "FastAPI + Supabase + Gemini ready!"}

# Add message to Supabase
@app.post("/add_message/")
def add_message(username: str = Query(...), message: str = Query(...)):
    try:
        data = {"username": username, "message": message}
        response = supabase.table("messages").insert(data).execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all messages
@app.get("/get_messages/")
def get_messages():
    try:
        response = supabase.table("messages").select("*").execute()
        return {"messages": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chatbot endpoint
@app.get("/chat/")
def chat(message: str = Query(...)):
    try:
        # Fetch company & sustainability info from Supabase
        company_details = supabase.table("company_details").select("*").execute().data or []
        company_locations = supabase.table("company_locations").select("*").execute().data or []
        services_products = supabase.table("services_products").select("*").execute().data or []

        # Few-shot prompt with company context
        few_shot_prompt = f"""
You are an AI assistant specializing in sustainability and company-related sustainability.
Answer questions in detail if they relate to sustainability, environmental regulations, or the company's sustainability initiatives.
If a question is unrelated to sustainability, respond politely: 'Please ask questions about sustainability.'

Company Details: {company_details}
Company Locations: {company_locations}
Products & Services: {services_products}

Examples:
Q: What are the main things I need to know about sustainability?
A: The main things you need to know about sustainability are: 1. Definition: Sustainability is about meeting present needs without compromising future generations' ability to meet theirs. 2. Three pillars: Environmental, social, and economic sustainability. 3. Key issues: Climate change, resource depletion, biodiversity loss, pollution, and social inequality. 4. Solutions: Renewable energy, circular economy, sustainable agriculture, and responsible consumption. 5. Individual action: Reducing waste, conserving energy, and making eco-friendly choices. 6. Business role: Adopting sustainable practices, innovating green technologies, and corporate social responsibility. 7. Global efforts: International agreements like the Paris Agreement and UN Sustainable Development Goals. 8. Long-term thinking: Considering the long-term impacts of our actions on the planet and society.

Q: What is sustainability?
A: Sustainability refers to the practice of meeting present needs without compromising the ability of future generations to meet their own needs. It involves environmental protection, social equity, and economic viability.

Q: What is EUDR?
A: EUDR stands for the European Union Deforestation Regulation. It's a sustainability-focused regulation that prevents deforestation-linked products from entering the EU market.

Q: What is carbon?
A: Carbon is a crucial element in sustainability discussions. It is important to understand carbon footprints, carbon cycle, and carbon neutrality for sustainability.

User Question: {message}
"""

        # Generate response from Gemini AI
        response = model.generate_content(
            contents=[few_shot_prompt]
        )

        answer = response.text.strip()

        # Log AI response to Supabase
        supabase.table("messages").insert({"username": "AI", "message": answer}).execute()

        return {"user_message": message, "ai_response": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))