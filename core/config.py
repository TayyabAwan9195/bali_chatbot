# ============================================================
# FILE: config.py
# PURPOSE: Configuration constants and settings
# ============================================================

import os

# Optional: dotenv for API keys
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v

# Database
DB_FILE = "leads.db"

# Groq API settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_MAX_TOKENS = 150
GROQ_TEMPERATURE = 0.2

# RAG settings
RAG_TOP_K = 5
FAQ_CONFIDENCE_THRESHOLD = 0.5
RAG_CONFIDENCE_THRESHOLD = 0.8

# History limits
MAX_HISTORY_MESSAGES = 6
MAX_HISTORY_DB = 10

# Rate limiting
MAX_MESSAGES_PER_MINUTE = 20

# System prompt for Groq
SYSTEM_PROMPT = (
    "You are a customer service assistant for Bali Legal Partner. Answer ONLY using the provided context.\n"
    "Rules:\n"
    "- Maximum 80 words per answer\n"
    "- Never add information not in the context\n"
    "- Never ask multiple questions at once\n"
    "- End with ONE simple follow-up question only\n"
    "- If not in context say: I specialize in PT PMA company setup, investor visas, and business services in Indonesia. Can I help with those?"
)

# Welcome menu message
MENU_MESSAGE = (
    "Hello! 👋 Welcome to Bali Legal Partner.\n\n"
    "We assist foreigners with:\n"
    "- Company setup (PT PMA)\n"
    "- Investor visas (KITAS)\n"
    "- Business licensing\n"
    "- Tax & accounting services\n\n"
    "How can I help you today?\n\n"
    "1️⃣ Open a company\n"
    "2️⃣ Investor visa\n"
    "3️⃣ Business licenses\n"
    "4️⃣ Accounting services"
)