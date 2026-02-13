import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print(f"Používám klíč začínající na: {api_key[:5]}...")
print("--- Hledám dostupné modely ---")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Nalezen model: {m.name}")
except Exception as e:
    print(f"❌ Chyba: {e}")