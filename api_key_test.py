# ============================================================
# API KEY TESTER
# Run: python test_api.py
# ============================================================

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

def test_openai():
    print("\n--- Testing OpenAI ---")
    try:
        from openai import OpenAI
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            print("❌ OPENAI_API_KEY not found in .env")
            return
        client = OpenAI(api_key=key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say hello"}]
        )
        print("✅ OpenAI working:", resp.choices[0].message.content.strip())
    except Exception as e:
        print("❌ OpenAI failed:", str(e)[:100])

def test_groq():
    print("\n--- Testing Groq ---")
    try:
        from groq import Groq
        key = os.getenv("GROQ_API_KEY")
        if not key:
            print("❌ GROQ_API_KEY not found in .env")
            return
        client = Groq(api_key=key)
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say hello"}]
        )
        print("✅ Groq working:", resp.choices[0].message.content.strip())
    except Exception as e:
        print("❌ Groq failed:", str(e)[:100])

def test_gemini():
    print("\n--- Testing Gemini ---")
    try:
        from google import genai
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            print("❌ GEMINI_API_KEY not found in .env")
            return
        client = genai.Client(api_key=key)
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say hello"
        )
        print("✅ Gemini working:", resp.text.strip()[:50])
    except Exception as e:
        print("❌ Gemini failed:", str(e)[:100])

if __name__ == "__main__":
    print("=" * 40)
    print("API KEY TESTER")
    print("=" * 40)
    test_openai()
    test_groq()
    test_gemini()
    print("\n" + "=" * 40)
    print("Done!")