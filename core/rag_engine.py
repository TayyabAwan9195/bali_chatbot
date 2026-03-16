# ============================================================
# FILE: rag_engine.py
# PURPOSE: Groq API integration for RAG responses
# ============================================================

import logging
import os
from typing import List, Optional
from groq import Groq
from core.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_MAX_TOKENS,
    GROQ_TEMPERATURE,
    SYSTEM_PROMPT,
    MAX_HISTORY_MESSAGES
)

# --- Client setup ---
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- Main function ---
def generate_with_context(
    question: str,
    contexts: List[str],
    history: Optional[list] = None,
) -> str:
    full_context = "\n\n".join(contexts)

    # Build messages
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    recent_history = history[-MAX_HISTORY_MESSAGES:] if history else []
    for msg in recent_history:
        if isinstance(msg, dict) and "role" in msg and "content" in msg and msg["role"] in ["user", "assistant"]:
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Add the user question with context as the last message
    messages.append(
        {
            "role": "user",
            "content": (
                f"Context:\n{full_context}\n\n"
                f"Question:\n{question}"
            ),
        }
    )

    if client is None:
        return "I'm having technical difficulties, please try again shortly."

    try:
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=GROQ_MAX_TOKENS,
            temperature=GROQ_TEMPERATURE,
            messages=messages,
        )
        return resp.choices[0].message.content.strip()
    except Exception as exc:
        logging.exception("Groq request failed")
        return "I'm having technical difficulties, please try again shortly."